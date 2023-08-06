#!/usr/bin/env python3

from heaserver.account import service
from heaserver.service.testcase import swaggerui
from integrationtests.heaserver.accountintegrationtest.testcase import db_store
from aiohttp.web import get, delete, post, put, view
from heaserver.service.testcase.testenv import MicroserviceContainerConfig, DockerVolumeMapping
from heaserver.service.testcase.dockermongo import DockerMongoManager
from heaserver.service.db.aws import S3Manager
from heaserver.service.wstl import builder_factory
import logging
from heaobject.volume import DEFAULT_FILE_SYSTEM
from heaobject.registry import Resource
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

HEASERVER_REGISTRY_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-registry:1.0.0a32'
HEASERVER_VOLUMES_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-volumes:1.0.0a17'
HEASERVER_KEYCHAIN_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-keychain:1.0.0a12'
HEASERVER_BUCKETS_IMAGE = 'registry.gitlab.com/huntsman-cancer-institute/risr/hea/heaserver-buckets:1.0.0a17'

if __name__ == '__main__':
    volume_microservice = MicroserviceContainerConfig(image=HEASERVER_VOLUMES_IMAGE, port=8080, check_path='/volumes',
                                                      db_manager_cls=DockerMongoManager,
                                                      resources=[Resource(resource_type_name='heaobject.volume.Volume',
                                                                          base_path='/volumes',
                                                                          file_system_name=DEFAULT_FILE_SYSTEM),
                                                                 Resource(
                                                                     resource_type_name='heaobject.volume.FileSystem',
                                                                     base_path='/filesystems',
                                                                     file_system_name=DEFAULT_FILE_SYSTEM)])
    keychain_microservice = MicroserviceContainerConfig(image=HEASERVER_KEYCHAIN_IMAGE, port=8080,
                                                        check_path='/credentials',
                                                        db_manager_cls=DockerMongoManager,
                                                        resources=[Resource(
                                                            resource_type_name='heaobject.keychain.Credentials',
                                                            base_path='/credentials',
                                                            file_system_name=DEFAULT_FILE_SYSTEM)])
    bucket_microservice = MicroserviceContainerConfig(image=HEASERVER_BUCKETS_IMAGE, port=8080, check_path='/ping',
                                                      db_manager_cls=DockerMongoManager,
                                                      # Switch to S3Manager for version 1.0.0a6.
                                                      resources=[
                                                          Resource(resource_type_name='heaobject.bucket.AWSBucket',
                                                                   base_path='/volumes',
                                                                   file_system_type="heaobject.volume.AWSFileSystem",
                                                                   file_system_name=DEFAULT_FILE_SYSTEM),
                                                          Resource(resource_type_name='heaobject.folder.AWSS3BucketItem',
                                                                   base_path='/volumes',
                                                                   file_system_type="heaobject.volume.AWSFileSystem",
                                                                   file_system_name=DEFAULT_FILE_SYSTEM)
                                                      ],
                                                      volumes=[DockerVolumeMapping(host=str(Path.home() / '.aws'),
                                                                                   container='/home/app/.aws')])
    swaggerui.run(project_slug='heaserver-accounts', desktop_objects=db_store,
                  wstl_builder_factory=builder_factory(service.__package__),
                  routes=[(get, '/volumes/{volume_id}/awsaccounts/me', service.get_awsaccount_by_volume_id),
                          (get, '/awsaccounts/{id}', service.get_awsaccount),
                          (get, '/awsaccounts/byname/{name}', service.get_awsaccount_by_name),
                          (get, '/awsaccounts', service.get_awsaccounts),
                          (view, '/volumes/{volume_id}/awsaccounts/me/opener',
                           service.get_awsaccount_opener_by_volume_id),
                          (view, '/awsaccounts/{id}/opener', service.get_awsaccount_opener),
                          (get, '/volumes/{volume_id}/awsaccounts/me/bucketitems', service.get_bucketitems_by_volume_id),
                          (view, '/volumes/{volume_id}/awsaccounts/me/creator', service.get_account_creator_by_volume_id),
                          (get, '/volumes/{volume_id}/awsaccounts/me/newbucket', service.get_new_bucket_form_by_volume_id),
                          (post, '/volumes/{volume_id}/awsaccounts/me/newbucket', service.post_new_bucket_by_volume_id),
                          (get, '/awsaccounts/{id}/buckets', service.get_buckets),
                          (view, '/awsaccounts/{id}/creator', service.get_account_creator),
                          (get, '/awsaccounts/{id}/newbucket', service.get_new_bucket_form),
                          (post, '/awsaccounts/{id}/newbucket', service.post_new_bucket)
                          ],
                  registry_docker_image=HEASERVER_REGISTRY_IMAGE,
                  other_docker_images=[keychain_microservice, volume_microservice, bucket_microservice],
                  db_manager_cls=S3Manager)
