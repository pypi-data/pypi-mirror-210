# -*- coding: utf-8 -*-
# Copyright (C) 2014 the2nd <the2nd@otpme.org>
# Distributed under the terms of the GNU General Public License v2
import os
import time
import random

try:
    if os.environ['OTPME_DEBUG_MODULE_LOADING'] == "True":
        print(_("Loading module: %s") % __name__)
except:
    pass

from otpme.lib import oid
from otpme.lib import stuff
#from otpme.lib import cache
from otpme.lib import config
from otpme.lib import backend
from otpme.lib import connections
from otpme.lib import sign_key_cache
from otpme.lib import multiprocessing
from otpme.lib.protocols import status_codes
from otpme.lib.protocols.otpme_server import OTPmeServer1
from otpme.lib.freeradius import reload as freeradius_reload

from otpme.lib.exceptions import *

logger = config.logger

REGISTER_BEFORE = []
REGISTER_AFTER = ['otpme.lib.protocols.otpme_server']
PROTOCOL_VERSION = "OTPme-cluster-1.0"

def register():
    config.register_otpme_protocol("clusterd", PROTOCOL_VERSION, server=True)

class OTPmeClusterP1(OTPmeServer1):
    """ Class that implements OTPme-cluster-1.0. """
    def __init__(self, **kwargs):
        # Our name.
        self.name = "clusterd"
        # The protocol we support.
        self.protocol = PROTOCOL_VERSION
        # Indicates parent class that we need no authentication.
        self.require_auth = "host"
        self.require_preauth = False
        self.require_client_cert = True
        # Communication with hostd is only done via unix sockets.
        self.encrypt_session = True
        # Require a consistent cluster state.
        self.require_quorum = False
        self.require_master_node = False
        # Call parent class init.
        OTPmeServer1.__init__(self, **kwargs)

    def _pre_init(self, *args, **kwargs):
        """ Init protocol handler. """
        # Our PID.
        self.pid = os.getpid()
        # Do atfork stuff.
        multiprocessing.atfork(quiet=True)

    def verify_peer(self):
        """ Verify peer. """
        if self.peer.type != "node":
            msg = "Peer is not a node."
            raise OTPmeException(msg)
        if self.peer.realm != config.realm:
            msg = "Peer is not from our realm: %s" % self.peer.realm
            raise OTPmeException(msg)
        if self.peer.site != config.site:
            msg = "Peer is not from our site: %s" % self.peer.site
            raise OTPmeException(msg)
        if not self.peer.enabled:
            msg = "Peer is disabled: %s" % self.peer.name
            raise HostDisabled(msg)

    def _process(self, command, command_args):
        """ Handle commands received from host_handler. """
        # all valid commands
        valid_commands = [
                            "ping",
                            "sync",
                            "write",
                            "rename",
                            "delete",
                            "get_node_vote",
                            "get_master_node",
                            "do_radius_reload",
                            "get_cluster_nodes",
                            "do_master_failover",
                            "get_cluster_quorum",
                            "get_node_sync_status",
                            "start_master_failover",
                            "get_master_sync_status",
                            "deconfigure_floating_ip",
                            "get_master_failover_status",
                        ]

        if command in valid_commands:
            pass
            #msg = ("Received command %s from client: %s"
            #        % (command, self.client))
            #logger.debug(msg)
        else:
            msg = ("Received unknown command %s from client: %s"
                    % (command, self.client))
            logger.warning(msg)

        # Make sure peer is a node from our site.
        try:
            self.verify_peer()
        except HostDisabled as e:
            status = status_codes.HOST_DISABLED
            message = "Failed to verify peer: %s: %s" % (self.peer, e)
            response = self.build_response(status, message, encrypt=False)
            return response
        except Exception as e:
            status = False
            message = "Failed to verify peer: %s: %s" % (self.peer, e)
            response = self.build_response(status, message, encrypt=False)
            return response

        # check if we got a valid command
        if not command in valid_commands:
            message = "Unknown command: %s" % command
            status = False

        elif command == "ping":
            message = "pong"
            status = True
            msg = "Received ping."
            logger.debug(msg)

        elif command == "get_master_node":
            try:
                message = multiprocessing.master_node['master']
                status = True
            except KeyError:
                message = None
                status = False

        elif command == "get_cluster_quorum":
            status = True
            try:
                cluster_quorum = config.cluster_quorum
            except:
                cluster_quorum = False
            message = cluster_quorum
            if cluster_quorum:
                try:
                    message = multiprocessing.cluster_quorum['quorum']
                except KeyError:
                    message = cluster_quorum

        elif command == "get_master_sync_status":
            if config.host_data['name'] in multiprocessing.master_sync_done:
                status = True
                message = "Master sync done."
            else:
                status = False
                message = "Master sync not done."

        elif command == "get_node_sync_status":
            status = True
            message = None
            try:
                node_name = command_args['node_name']
            except:
                message = "Missing node name."
                status = False
            if status:
                if node_name not in multiprocessing.init_sync_done:
                    status = False

        elif command == "get_node_vote":
            status = True
            message = 0.0
            # Get/set vote for this node. This is also done in clusterd daemon.
            if config.cluster_vote_participation:
                try:
                    message = multiprocessing.node_votes[config.host_data['name']]
                except:
                    node_vote = random.random()
                    current_master_node = stuff.get_master_node()
                    if self.host_name == current_master_node:
                        node_vote += 1
                    multiprocessing.node_votes[config.host_data['name']] = node_vote
                    message = node_vote

        elif command == "get_cluster_nodes":
            status = True
            message = multiprocessing.node_votes.keys()

        elif command == "sync":
            status = True
            message = None
            try:
                remote_objects = command_args['remote_objects']
            except:
                message = "Missing remote objects."
                status = False
            if status:
                object_types = config.get_cluster_object_types()
                result = backend.search(object_types=object_types,
                                        attribute="uuid",
                                        value="*",
                                        return_type="instance")
                sync_objects = {}
                for x in result:
                    sync_object = False
                    try:
                        remote_object_data = remote_objects[x.oid.full_oid]
                    except:
                        remote_object_data = None
                        sync_object = True
                    if remote_object_data:
                        remote_last_used = remote_object_data['last_used']
                        if remote_last_used is not None and x.last_used is not None:
                            if remote_last_used < x.last_used:
                                sync_object = True
                        remote_last_modified = remote_object_data['last_modified']
                        if remote_last_modified is not None and x.last_modified is not None:
                            if remote_last_modified < x.last_modified:
                                sync_object = True
                    if not sync_object:
                        continue
                    sync_objects[x.oid.full_oid] = {}
                    sync_objects[x.oid.full_oid]['last_used'] = x.last_used
                    sync_objects[x.oid.full_oid]['last_modified'] = x.last_modified
                    sync_objects[x.oid.full_oid]['object_config'] = x.object_config.copy()
                message = sync_objects
                msg = ("Sending %s objects to peer: %s"
                        % (len(sync_objects), self.peer.name))
                logger.info(msg)

        elif command == "write":
            status = True
            message = None
            try:
                object_id = command_args['object_id']
            except:
                message = "Missing object ID."
                status = False
            try:
                object_config = command_args['object_config']
            except:
                message = "Missing object config."
                status = False
            try:
                last_modified = command_args['last_modified']
            except:
                last_modified = None
            try:
                last_used = command_args['last_used']
            except:
                last_used = None
            if status:
                write_object = True
                object_id = oid.get(object_id)
                if last_modified is not None:
                    local_object = backend.get_object(object_id)
                    if local_object:
                        if local_object.last_modified > last_modified:
                            write_object = False
                if write_object:
                    msg = "Writing object: %s" % object_id
                    logger.debug(msg)
                    if last_used is not None:
                        object_uuid = object_config['UUID']
                        if last_used is not None:
                            backend.set_last_used(object_id.realm,
                                                object_id.site,
                                                object_id.object_type,
                                                object_uuid, last_used)
                    try:
                        backend.write_config(object_id=object_id,
                                            index_auto_update=True,
                                            full_data_update=True,
                                            object_config=object_config)
                        status = True
                        message = "done"
                    except Exception as e:
                        message = "Failed to write object: %s: %s" % (object_id, e)
                        logger.warning(message)

                # Update signers cache.
                if object_id.object_type == "user":
                    new_object = backend.get_object(object_id)
                    if new_object.public_key:
                        try:
                            public_key = sign_key_cache.get_cache(object_id)
                        except Exception as e:
                            msg = "Unable to read signer cache: %s: %s" % (object_id, e)
                            self.logger.critical(msg)
                            public_key = None
                        if new_object.public_key != public_key:
                            try:
                                sign_key_cache.add_cache(object_id, new_object.public_key)
                            except Exception as e:
                                msg = "Unable to add signer cache: %s: %s" % (object_id, e)
                                self.logger.critical(msg)
                    else:
                        try:
                            public_key = sign_key_cache.get_cache(object_id)
                        except Exception as e:
                            msg = "Unable to read signer cache: %s: %s" % (object_id, e)
                            self.logger.critical(msg)
                            public_key = None
                        if public_key:
                            try:
                                sign_key_cache.del_cache(object_id)
                            except Exception as e:
                                msg = "Unable to add signer cache: %s: %s" % (object_id, e)
                                self.logger.critical(msg)

        elif command == "rename":
            status = True
            message = None
            try:
                object_id = command_args['object_id']
            except:
                message = "Missing object ID."
                status = False
            try:
                new_object_id = command_args['new_object_id']
            except:
                message = "Missing new object ID."
                status = False
            if status:
                msg = "Renaming object: %s: %s" % (object_id, new_object_id)
                logger.debug(msg)
                object_id = oid.get(object_id)
                new_object_id = oid.get(new_object_id)
                try:
                    backend.rename_object(object_id, new_object_id)
                    status = True
                    message = "done"
                except Exception as e:
                    message = "Failed to rename object: %s: %s" % (object_id, e)
                    logger.warning(message)

        elif command == "delete":
            status = True
            message = "done"
            try:
                object_uuid = command_args['object_uuid']
            except:
                message = "Missing object UUID."
                status = False
            if status:
                try:
                    object_id = backend.get_oid(object_uuid, instance=True)
                except Exception as e:
                    status = False
            if status and object_id:
                if object_id.object_type == "user":
                    try:
                        public_key = sign_key_cache.get_cache(object_id)
                    except Exception as e:
                        msg = "Unable to read signer cache: %s: %s" % (object_id, e)
                        self.logger.critical(msg)
                        public_key = None
                    if public_key:
                        try:
                            sign_key_cache.del_cache(object_id)
                        except Exception as e:
                            msg = "Unable to add signer cache: %s: %s" % (object_id, e)
                            self.logger.critical(msg)
                msg = "Removing object: %s" % object_id
                logger.debug(msg)
                try:
                    backend.delete_object(object_id=object_id)
                    status = True
                    message = "done"
                except UnknownObject:
                    status = True
                    message = "Unknown object."
                except Exception as e:
                    message = "Failed to delete object: %s: %s" % (object_id, e)
                    logger.warning(message)

        elif command == "deconfigure_floating_ip":
            status = True
            message = "Floating IP deconfigured."
            msg = "Received request to deconfigure floating IP."
            logger.info(msg)
            try:
                self.comm_handler.send("controld", command="deconfigure_floating_ip")
            except Exception as e:
                status = False
                message = "Failed to send deconfigure floating IP request."
                msg = "Failed to send deconfigure floating IP request: %s" % e
                logger.critical(msg)

        elif command == "start_master_failover":
            status = True
            message = "Master failover started successful."
            config.cluster_status = False

        elif command == "get_master_failover_status":
            message = "Master failover status."
            status = config.master_failover

        elif command == "do_radius_reload":
            try:
                freeradius_reload()
                status = True
            except Exception as e:
                message = "Radius reload failed: %s" % e
                status = False

        elif command == "do_master_failover":
            status = True
            message = "Master failover request successful."
            if config.master_failover:
                status = False
                message = "Ongoing master_failover."
            if status:
                msg = "Staring master failover..."
                logger.info(msg)
                config.master_failover = True
                config.cluster_status = False
                result = backend.search(object_type="node",
                                        attribute="uuid",
                                        value="*",
                                        realm=config.realm,
                                        site=config.site,
                                        return_type="instance")
                for x_node in result:
                    if not x_node.enabled:
                        continue
                    if x_node.name == config.host_data['name']:
                        continue
                    try:
                        socket_uri = stuff.get_daemon_socket("clusterd", x_node.name)
                    except Exception as e:
                        msg = "Failed to get clusterd socket: %s: %s" % (x_node.name, e)
                        logger.critical(msg)
                        continue
                    try:
                        clusterd_conn = connections.get("clusterd", socket_uri=socket_uri)
                    except Exception as e:
                        msg = "Cluster connection failed: %s: %s" % (x_node.name, e)
                        logger.critical(msg)
                        continue
                    try:
                        clusterd_conn.start_master_failover()
                    except Exception as e:
                        msg = "Master failover failed: %s: %s" % (x_node.name, e)
                        logger.critical(msg)

            # Do final sync.
            if status:
                from otpme.lib.classes.command_handler import CommandHandler
                command_handler = CommandHandler()
                while True:
                    try:
                        sync_status = command_handler.do_sync(sync_type="objects",
                                                            realm=config.realm,
                                                            site=config.site,
                                                            max_tries=3)
                    except Exception as e:
                        msg = "Final sync of objects failed: %s" % e
                        logger.warning(msg)
                        sync_status = False
                    if sync_status is not False:
                        break

            if status:
                site_oid = "site|%s/%s" % (config.realm, config.site)
                site_oid = oid.get(site_oid)
                try:
                    site = backend.get_object(object_id=site_oid)
                except Exception as e:
                    status = False
                    message = "Failed to load site: %s: %s" % (site_oid, e)
                    logger.warning(message)
            if status:
                try:
                    site.master_failover(config.host_data['name'])
                except AlreadyMaster:
                    pass
                except Exception as e:
                    status = False
                    message = "Failed to do master failover: %s" % e
                    logger.warning(message)
            if status:
                new_master_vote = max(multiprocessing.node_votes.values())
                new_master_vote = new_master_vote + (new_master_vote / 10)
                multiprocessing.node_votes[config.host_data['name']] = new_master_vote
                while True:
                    try:
                        master_node = multiprocessing.master_node['master']
                    except:
                        time.sleep(0.01)
                        continue
                    if master_node != self.host_name:
                        print("Waiting for node to get master node...")
                        time.sleep(1)
                        continue
                    break

        response = self.build_response(status, message, encrypt=False)
        return response

    def _close(self):
        pass
