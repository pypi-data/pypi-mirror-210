# coding: utf-8

from __future__ import absolute_import

import importlib

from huaweicloudsdkcore.client import Client, ClientBuilder
from huaweicloudsdkcore.utils import http_utils
from huaweicloudsdkcore.sdk_stream_request import SdkStreamRequest


class EgAsyncClient(Client):
    def __init__(self):
        super(EgAsyncClient, self).__init__()
        self.model_package = importlib.import_module("huaweicloudsdkeg.v1.model")

    @classmethod
    def new_builder(cls, clazz=None):
        if clazz is None:
            return ClientBuilder(cls)

        if clazz.__name__ != "EgClient":
            raise TypeError("client type error, support client type is EgClient")

        return ClientBuilder(clazz)

    def check_put_events_async(self, request):
        """预校验指定事件源发布事件成功

        发布事件到事件源成功需要有订阅等条件，预先校验
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CheckPutEvents
        :type request: :class:`huaweicloudsdkeg.v1.CheckPutEventsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CheckPutEventsResponse`
        """
        return self._check_put_events_with_http_info(request)

    def _check_put_events_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/events/check',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CheckPutEventsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def create_agencies_async(self, request):
        """创建服务委托

        按照业务场景，一键创建服务委托授权
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CreateAgencies
        :type request: :class:`huaweicloudsdkeg.v1.CreateAgenciesRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CreateAgenciesResponse`
        """
        return self._create_agencies_with_http_info(request)

    def _create_agencies_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/service-agencies',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CreateAgenciesResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def create_channel_async(self, request):
        """创建自定义事件通道

        创建自定义事件通道
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CreateChannel
        :type request: :class:`huaweicloudsdkeg.v1.CreateChannelRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CreateChannelResponse`
        """
        return self._create_channel_with_http_info(request)

    def _create_channel_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/channels',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CreateChannelResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def create_connection_async(self, request):
        """创建目标连接

        创建目标连接
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CreateConnection
        :type request: :class:`huaweicloudsdkeg.v1.CreateConnectionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CreateConnectionResponse`
        """
        return self._create_connection_with_http_info(request)

    def _create_connection_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/connections',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CreateConnectionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def create_endpoint_async(self, request):
        """创建访问端点

        创建访问端点
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CreateEndpoint
        :type request: :class:`huaweicloudsdkeg.v1.CreateEndpointRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CreateEndpointResponse`
        """
        return self._create_endpoint_with_http_info(request)

    def _create_endpoint_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/endpoints',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CreateEndpointResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def create_event_schema_async(self, request):
        """创建自定义事件模型

        创建自定义事件模型
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CreateEventSchema
        :type request: :class:`huaweicloudsdkeg.v1.CreateEventSchemaRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CreateEventSchemaResponse`
        """
        return self._create_event_schema_with_http_info(request)

    def _create_event_schema_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schemas',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CreateEventSchemaResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def create_event_schema_version_async(self, request):
        """创建自定义事件模型版本

        创建自定义事件模型版本，版本号后台自动生成
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CreateEventSchemaVersion
        :type request: :class:`huaweicloudsdkeg.v1.CreateEventSchemaVersionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CreateEventSchemaVersionResponse`
        """
        return self._create_event_schema_version_with_http_info(request)

    def _create_event_schema_version_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'schema_id' in local_var_params:
            path_params['schema_id'] = local_var_params['schema_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schemas/{schema_id}/versions',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CreateEventSchemaVersionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def create_event_source_async(self, request):
        """创建自定义事件源

        创建用户自定义类型的事件源，只能指定自定义通道，不能指定系统通道
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CreateEventSource
        :type request: :class:`huaweicloudsdkeg.v1.CreateEventSourceRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CreateEventSourceResponse`
        """
        return self._create_event_source_with_http_info(request)

    def _create_event_source_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/sources',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CreateEventSourceResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def create_subscription_async(self, request):
        """创建事件订阅

        创建事件订阅
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CreateSubscription
        :type request: :class:`huaweicloudsdkeg.v1.CreateSubscriptionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CreateSubscriptionResponse`
        """
        return self._create_subscription_with_http_info(request)

    def _create_subscription_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CreateSubscriptionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def create_subscription_target_async(self, request):
        """创建事件订阅目标

        创建单个事件订阅目标
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for CreateSubscriptionTarget
        :type request: :class:`huaweicloudsdkeg.v1.CreateSubscriptionTargetRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.CreateSubscriptionTargetResponse`
        """
        return self._create_subscription_target_with_http_info(request)

    def _create_subscription_target_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in local_var_params:
            path_params['subscription_id'] = local_var_params['subscription_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/{subscription_id}/targets',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='CreateSubscriptionTargetResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def delete_channel_async(self, request):
        """删除自定义事件通道

        删除指定自定义事件通道
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for DeleteChannel
        :type request: :class:`huaweicloudsdkeg.v1.DeleteChannelRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.DeleteChannelResponse`
        """
        return self._delete_channel_with_http_info(request)

    def _delete_channel_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'channel_id' in local_var_params:
            path_params['channel_id'] = local_var_params['channel_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/channels/{channel_id}',
            method='DELETE',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='DeleteChannelResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def delete_connection_async(self, request):
        """删除目标连接

        删除目标连接
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for DeleteConnection
        :type request: :class:`huaweicloudsdkeg.v1.DeleteConnectionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.DeleteConnectionResponse`
        """
        return self._delete_connection_with_http_info(request)

    def _delete_connection_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'connection_id' in local_var_params:
            path_params['connection_id'] = local_var_params['connection_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/connections/{connection_id}',
            method='DELETE',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='DeleteConnectionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def delete_endpoint_async(self, request):
        """删除访问端点

        删除访问端点
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for DeleteEndpoint
        :type request: :class:`huaweicloudsdkeg.v1.DeleteEndpointRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.DeleteEndpointResponse`
        """
        return self._delete_endpoint_with_http_info(request)

    def _delete_endpoint_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'endpoint_id' in local_var_params:
            path_params['endpoint_id'] = local_var_params['endpoint_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/endpoints/{endpoint_id}',
            method='DELETE',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='DeleteEndpointResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def delete_event_schema_async(self, request):
        """删除事件模型

        删除事件模型
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for DeleteEventSchema
        :type request: :class:`huaweicloudsdkeg.v1.DeleteEventSchemaRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.DeleteEventSchemaResponse`
        """
        return self._delete_event_schema_with_http_info(request)

    def _delete_event_schema_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'schema_id' in local_var_params:
            path_params['schema_id'] = local_var_params['schema_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schemas/{schema_id}',
            method='DELETE',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='DeleteEventSchemaResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def delete_event_schema_version_async(self, request):
        """删除事件模型版本

        删除事件模型指定版本
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for DeleteEventSchemaVersion
        :type request: :class:`huaweicloudsdkeg.v1.DeleteEventSchemaVersionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.DeleteEventSchemaVersionResponse`
        """
        return self._delete_event_schema_version_with_http_info(request)

    def _delete_event_schema_version_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'schema_id' in local_var_params:
            path_params['schema_id'] = local_var_params['schema_id']
        if 'version' in local_var_params:
            path_params['version'] = local_var_params['version']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schemas/{schema_id}/versions/{version}',
            method='DELETE',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='DeleteEventSchemaVersionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def delete_event_source_async(self, request):
        """删除自定义事件源

        删除指定的自定义事件源
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for DeleteEventSource
        :type request: :class:`huaweicloudsdkeg.v1.DeleteEventSourceRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.DeleteEventSourceResponse`
        """
        return self._delete_event_source_with_http_info(request)

    def _delete_event_source_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'source_id' in local_var_params:
            path_params['source_id'] = local_var_params['source_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/sources/{source_id}',
            method='DELETE',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='DeleteEventSourceResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def delete_subscription_async(self, request):
        """删除事件订阅

        删除事件订阅
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for DeleteSubscription
        :type request: :class:`huaweicloudsdkeg.v1.DeleteSubscriptionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.DeleteSubscriptionResponse`
        """
        return self._delete_subscription_with_http_info(request)

    def _delete_subscription_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in local_var_params:
            path_params['subscription_id'] = local_var_params['subscription_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/{subscription_id}',
            method='DELETE',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='DeleteSubscriptionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def delete_subscription_target_async(self, request):
        """删除事件订阅目标

        删除事件订阅目标
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for DeleteSubscriptionTarget
        :type request: :class:`huaweicloudsdkeg.v1.DeleteSubscriptionTargetRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.DeleteSubscriptionTargetResponse`
        """
        return self._delete_subscription_target_with_http_info(request)

    def _delete_subscription_target_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in local_var_params:
            path_params['subscription_id'] = local_var_params['subscription_id']
        if 'target_id' in local_var_params:
            path_params['target_id'] = local_var_params['target_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/{subscription_id}/targets/{target_id}',
            method='DELETE',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='DeleteSubscriptionTargetResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def discover_event_schema_from_data_async(self, request):
        """事件模型自动发现

        事件模型自动发现
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for DiscoverEventSchemaFromData
        :type request: :class:`huaweicloudsdkeg.v1.DiscoverEventSchemaFromDataRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.DiscoverEventSchemaFromDataResponse`
        """
        return self._discover_event_schema_from_data_with_http_info(request)

    def _discover_event_schema_from_data_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schema-discover',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='DiscoverEventSchemaFromDataResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_agencies_async(self, request):
        """查询服务委托

        查询服务委托
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListAgencies
        :type request: :class:`huaweicloudsdkeg.v1.ListAgenciesRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListAgenciesResponse`
        """
        return self._list_agencies_with_http_info(request)

    def _list_agencies_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'type' in local_var_params:
            query_params.append(('type', local_var_params['type']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/service-agencies',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListAgenciesResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_channels_async(self, request):
        """查询事件通道列表

        查询事件通道列表，包括系统通道和自定义通道
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListChannels
        :type request: :class:`huaweicloudsdkeg.v1.ListChannelsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListChannelsResponse`
        """
        return self._list_channels_with_http_info(request)

    def _list_channels_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))
        if 'provider_type' in local_var_params:
            query_params.append(('provider_type', local_var_params['provider_type']))
        if 'name' in local_var_params:
            query_params.append(('name', local_var_params['name']))
        if 'fuzzy_name' in local_var_params:
            query_params.append(('fuzzy_name', local_var_params['fuzzy_name']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/channels',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListChannelsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_connections_async(self, request):
        """查询目标连接列表

        查询目标连接列表
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListConnections
        :type request: :class:`huaweicloudsdkeg.v1.ListConnectionsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListConnectionsResponse`
        """
        return self._list_connections_with_http_info(request)

    def _list_connections_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))
        if 'name' in local_var_params:
            query_params.append(('name', local_var_params['name']))
        if 'fuzzy_name' in local_var_params:
            query_params.append(('fuzzy_name', local_var_params['fuzzy_name']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/connections',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListConnectionsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_endpoints_async(self, request):
        """查询访问端点

        查询访问端点
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListEndpoints
        :type request: :class:`huaweicloudsdkeg.v1.ListEndpointsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListEndpointsResponse`
        """
        return self._list_endpoints_with_http_info(request)

    def _list_endpoints_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))
        if 'type' in local_var_params:
            query_params.append(('type', local_var_params['type']))
        if 'name' in local_var_params:
            query_params.append(('name', local_var_params['name']))
        if 'vpc_id' in local_var_params:
            query_params.append(('vpc_id', local_var_params['vpc_id']))
        if 'fuzzy_name' in local_var_params:
            query_params.append(('fuzzy_name', local_var_params['fuzzy_name']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/endpoints',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListEndpointsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_event_schema_async(self, request):
        """查询事件模型列表

        查询事件模型列表，包括系统事件模型和自定义事件模型
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListEventSchema
        :type request: :class:`huaweicloudsdkeg.v1.ListEventSchemaRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListEventSchemaResponse`
        """
        return self._list_event_schema_with_http_info(request)

    def _list_event_schema_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))
        if 'provider_type' in local_var_params:
            query_params.append(('provider_type', local_var_params['provider_type']))
        if 'name' in local_var_params:
            query_params.append(('name', local_var_params['name']))
        if 'fuzzy_name' in local_var_params:
            query_params.append(('fuzzy_name', local_var_params['fuzzy_name']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schemas',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListEventSchemaResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_event_schema_versions_async(self, request):
        """查询事件模型版本列表

        查询事件模型版本列表
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListEventSchemaVersions
        :type request: :class:`huaweicloudsdkeg.v1.ListEventSchemaVersionsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListEventSchemaVersionsResponse`
        """
        return self._list_event_schema_versions_with_http_info(request)

    def _list_event_schema_versions_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'schema_id' in local_var_params:
            path_params['schema_id'] = local_var_params['schema_id']

        query_params = []
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schemas/{schema_id}/versions',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListEventSchemaVersionsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_event_sources_async(self, request):
        """查询事件源列表

        支持条件查询，如可以指定事件通道ID来查询某个事件通道下的所有事件源
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListEventSources
        :type request: :class:`huaweicloudsdkeg.v1.ListEventSourcesRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListEventSourcesResponse`
        """
        return self._list_event_sources_with_http_info(request)

    def _list_event_sources_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'channel_id' in local_var_params:
            query_params.append(('channel_id', local_var_params['channel_id']))
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))
        if 'provider_type' in local_var_params:
            query_params.append(('provider_type', local_var_params['provider_type']))
        if 'name' in local_var_params:
            query_params.append(('name', local_var_params['name']))
        if 'fuzzy_name' in local_var_params:
            query_params.append(('fuzzy_name', local_var_params['fuzzy_name']))
        if 'fuzzy_label' in local_var_params:
            query_params.append(('fuzzy_label', local_var_params['fuzzy_label']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/sources',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListEventSourcesResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_event_target_async(self, request):
        """查询事件目标分类

        查询预置的事件目标分类，获取每个事件目标分类的字段定义
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListEventTarget
        :type request: :class:`huaweicloudsdkeg.v1.ListEventTargetRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListEventTargetResponse`
        """
        return self._list_event_target_with_http_info(request)

    def _list_event_target_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))
        if 'fuzzy_label' in local_var_params:
            query_params.append(('fuzzy_label', local_var_params['fuzzy_label']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/target-catalogs',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListEventTargetResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_pub_metrics_async(self, request):
        """查询事件通道监控指标数据

        查询事件通道监控指标数据
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListPubMetrics
        :type request: :class:`huaweicloudsdkeg.v1.ListPubMetricsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListPubMetricsResponse`
        """
        return self._list_pub_metrics_with_http_info(request)

    def _list_pub_metrics_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'filter' in local_var_params:
            query_params.append(('filter', local_var_params['filter']))
        if 'period' in local_var_params:
            query_params.append(('period', local_var_params['period']))
        if 'start_time' in local_var_params:
            query_params.append(('start_time', local_var_params['start_time']))
        if 'end_time' in local_var_params:
            query_params.append(('end_time', local_var_params['end_time']))
        if 'channel_id' in local_var_params:
            query_params.append(('channel_id', local_var_params['channel_id']))
        if 'provider_type' in local_var_params:
            query_params.append(('provider_type', local_var_params['provider_type']))
        if 'source_name' in local_var_params:
            query_params.append(('source_name', local_var_params['source_name']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/metrics/pub',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListPubMetricsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_quotas_async(self, request):
        """查询配额

        查询当前租户的配额，未特殊配置过的会返回默认配额
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListQuotas
        :type request: :class:`huaweicloudsdkeg.v1.ListQuotasRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListQuotasResponse`
        """
        return self._list_quotas_with_http_info(request)

    def _list_quotas_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'type' in local_var_params:
            query_params.append(('type', local_var_params['type']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/quotas',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListQuotasResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_sub_metrics_async(self, request):
        """查询事件订阅监控指标数据

        查询事件订阅监控指标数据
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListSubMetrics
        :type request: :class:`huaweicloudsdkeg.v1.ListSubMetricsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListSubMetricsResponse`
        """
        return self._list_sub_metrics_with_http_info(request)

    def _list_sub_metrics_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'filter' in local_var_params:
            query_params.append(('filter', local_var_params['filter']))
        if 'period' in local_var_params:
            query_params.append(('period', local_var_params['period']))
        if 'start_time' in local_var_params:
            query_params.append(('start_time', local_var_params['start_time']))
        if 'end_time' in local_var_params:
            query_params.append(('end_time', local_var_params['end_time']))
        if 'subscription_id' in local_var_params:
            query_params.append(('subscription_id', local_var_params['subscription_id']))
        if 'provider_type' in local_var_params:
            query_params.append(('provider_type', local_var_params['provider_type']))
        if 'target_id' in local_var_params:
            query_params.append(('target_id', local_var_params['target_id']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/metrics/sub',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListSubMetricsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_subscriptions_async(self, request):
        """查询事件订阅列表

        查询事件订阅列表，支持指定事件通道
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListSubscriptions
        :type request: :class:`huaweicloudsdkeg.v1.ListSubscriptionsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListSubscriptionsResponse`
        """
        return self._list_subscriptions_with_http_info(request)

    def _list_subscriptions_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'channel_id' in local_var_params:
            query_params.append(('channel_id', local_var_params['channel_id']))
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))
        if 'name' in local_var_params:
            query_params.append(('name', local_var_params['name']))
        if 'fuzzy_name' in local_var_params:
            query_params.append(('fuzzy_name', local_var_params['fuzzy_name']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListSubscriptionsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_triggers_async(self, request):
        """查询单个函数的EG触发器

        查询触发器，支持指定函数urn。一个以函数urn为目标的订阅为一个触发器。
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListTriggers
        :type request: :class:`huaweicloudsdkeg.v1.ListTriggersRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListTriggersResponse`
        """
        return self._list_triggers_with_http_info(request)

    def _list_triggers_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'func_urn' in local_var_params:
            path_params['func_urn'] = local_var_params['func_urn']

        query_params = []
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscription-triggers/{func_urn}',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListTriggersResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_workflow_triggers_async(self, request):
        """查询单个函数流的EG触发器

        查询触发器，支持指定函数流id。一个以函数流id为目标的订阅为一个触发器。
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListWorkflowTriggers
        :type request: :class:`huaweicloudsdkeg.v1.ListWorkflowTriggersRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListWorkflowTriggersResponse`
        """
        return self._list_workflow_triggers_with_http_info(request)

    def _list_workflow_triggers_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'workflow_id' in local_var_params:
            path_params['workflow_id'] = local_var_params['workflow_id']

        query_params = []
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscription-triggers/workflow/{workflow_id}',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListWorkflowTriggersResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def operate_subscription_async(self, request):
        """操作事件订阅

        操作事件订阅，支持启用、禁用
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for OperateSubscription
        :type request: :class:`huaweicloudsdkeg.v1.OperateSubscriptionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.OperateSubscriptionResponse`
        """
        return self._operate_subscription_with_http_info(request)

    def _operate_subscription_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/operation',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='OperateSubscriptionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def put_events_async(self, request):
        """发布事件到事件通道

        发布事件到事件通道
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for PutEvents
        :type request: :class:`huaweicloudsdkeg.v1.PutEventsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.PutEventsResponse`
        """
        return self._put_events_with_http_info(request)

    def _put_events_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'channel_id' in local_var_params:
            path_params['channel_id'] = local_var_params['channel_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/channels/{channel_id}/events',
            method='POST',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='PutEventsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def show_detail_of_channel_async(self, request):
        """查询事件通道详情

        查询指定事件通道详情
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ShowDetailOfChannel
        :type request: :class:`huaweicloudsdkeg.v1.ShowDetailOfChannelRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ShowDetailOfChannelResponse`
        """
        return self._show_detail_of_channel_with_http_info(request)

    def _show_detail_of_channel_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'channel_id' in local_var_params:
            path_params['channel_id'] = local_var_params['channel_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/channels/{channel_id}',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ShowDetailOfChannelResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def show_detail_of_connection_async(self, request):
        """查询目标连接详情

        查询目标连接详情
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ShowDetailOfConnection
        :type request: :class:`huaweicloudsdkeg.v1.ShowDetailOfConnectionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ShowDetailOfConnectionResponse`
        """
        return self._show_detail_of_connection_with_http_info(request)

    def _show_detail_of_connection_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'connection_id' in local_var_params:
            path_params['connection_id'] = local_var_params['connection_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/connections/{connection_id}',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ShowDetailOfConnectionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def show_detail_of_event_schema_async(self, request):
        """查询事件模型详情

        查询事件模型详情
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ShowDetailOfEventSchema
        :type request: :class:`huaweicloudsdkeg.v1.ShowDetailOfEventSchemaRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ShowDetailOfEventSchemaResponse`
        """
        return self._show_detail_of_event_schema_with_http_info(request)

    def _show_detail_of_event_schema_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'schema_id' in local_var_params:
            path_params['schema_id'] = local_var_params['schema_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schemas/{schema_id}',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ShowDetailOfEventSchemaResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def show_detail_of_event_schema_version_async(self, request):
        """查询事件模型版本详情

        查询事件模型指定版本详情
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ShowDetailOfEventSchemaVersion
        :type request: :class:`huaweicloudsdkeg.v1.ShowDetailOfEventSchemaVersionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ShowDetailOfEventSchemaVersionResponse`
        """
        return self._show_detail_of_event_schema_version_with_http_info(request)

    def _show_detail_of_event_schema_version_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'schema_id' in local_var_params:
            path_params['schema_id'] = local_var_params['schema_id']
        if 'version' in local_var_params:
            path_params['version'] = local_var_params['version']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schemas/{schema_id}/versions/{version}',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ShowDetailOfEventSchemaVersionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def show_detail_of_event_source_async(self, request):
        """查询事件源详情

        查询事件源详情信息
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ShowDetailOfEventSource
        :type request: :class:`huaweicloudsdkeg.v1.ShowDetailOfEventSourceRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ShowDetailOfEventSourceResponse`
        """
        return self._show_detail_of_event_source_with_http_info(request)

    def _show_detail_of_event_source_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'source_id' in local_var_params:
            path_params['source_id'] = local_var_params['source_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/sources/{source_id}',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ShowDetailOfEventSourceResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def show_detail_of_subscription_async(self, request):
        """查询事件订阅详情

        查询事件订阅详情
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ShowDetailOfSubscription
        :type request: :class:`huaweicloudsdkeg.v1.ShowDetailOfSubscriptionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ShowDetailOfSubscriptionResponse`
        """
        return self._show_detail_of_subscription_with_http_info(request)

    def _show_detail_of_subscription_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in local_var_params:
            path_params['subscription_id'] = local_var_params['subscription_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/{subscription_id}',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ShowDetailOfSubscriptionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def show_detail_of_subscription_target_async(self, request):
        """查询事件订阅目标详情

        查询事件订阅目标详情
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ShowDetailOfSubscriptionTarget
        :type request: :class:`huaweicloudsdkeg.v1.ShowDetailOfSubscriptionTargetRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ShowDetailOfSubscriptionTargetResponse`
        """
        return self._show_detail_of_subscription_target_with_http_info(request)

    def _show_detail_of_subscription_target_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in local_var_params:
            path_params['subscription_id'] = local_var_params['subscription_id']
        if 'target_id' in local_var_params:
            path_params['target_id'] = local_var_params['target_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/{subscription_id}/targets/{target_id}',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ShowDetailOfSubscriptionTargetResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def update_channel_async(self, request):
        """更新自定义事件通道

        更新自定义事件通道定义
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for UpdateChannel
        :type request: :class:`huaweicloudsdkeg.v1.UpdateChannelRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.UpdateChannelResponse`
        """
        return self._update_channel_with_http_info(request)

    def _update_channel_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'channel_id' in local_var_params:
            path_params['channel_id'] = local_var_params['channel_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/channels/{channel_id}',
            method='PUT',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='UpdateChannelResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def update_connection_async(self, request):
        """更新目标连接

        更新目标连接
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for UpdateConnection
        :type request: :class:`huaweicloudsdkeg.v1.UpdateConnectionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.UpdateConnectionResponse`
        """
        return self._update_connection_with_http_info(request)

    def _update_connection_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'connection_id' in local_var_params:
            path_params['connection_id'] = local_var_params['connection_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/connections/{connection_id}',
            method='PUT',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='UpdateConnectionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def update_endpoint_async(self, request):
        """更新访问端点

        更新访问端点
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for UpdateEndpoint
        :type request: :class:`huaweicloudsdkeg.v1.UpdateEndpointRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.UpdateEndpointResponse`
        """
        return self._update_endpoint_with_http_info(request)

    def _update_endpoint_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'endpoint_id' in local_var_params:
            path_params['endpoint_id'] = local_var_params['endpoint_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/endpoints/{endpoint_id}',
            method='PUT',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='UpdateEndpointResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def update_event_schema_async(self, request):
        """更新自定义事件模型

        更新自定义事件模型定义
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for UpdateEventSchema
        :type request: :class:`huaweicloudsdkeg.v1.UpdateEventSchemaRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.UpdateEventSchemaResponse`
        """
        return self._update_event_schema_with_http_info(request)

    def _update_event_schema_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'schema_id' in local_var_params:
            path_params['schema_id'] = local_var_params['schema_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/schemas/{schema_id}',
            method='PUT',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='UpdateEventSchemaResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def update_event_source_async(self, request):
        """更新自定义事件源

        更新自定义事件源定义
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for UpdateEventSource
        :type request: :class:`huaweicloudsdkeg.v1.UpdateEventSourceRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.UpdateEventSourceResponse`
        """
        return self._update_event_source_with_http_info(request)

    def _update_event_source_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'source_id' in local_var_params:
            path_params['source_id'] = local_var_params['source_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/sources/{source_id}',
            method='PUT',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='UpdateEventSourceResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def update_subscription_async(self, request):
        """更新事件订阅

        更新事件订阅定义
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for UpdateSubscription
        :type request: :class:`huaweicloudsdkeg.v1.UpdateSubscriptionRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.UpdateSubscriptionResponse`
        """
        return self._update_subscription_with_http_info(request)

    def _update_subscription_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in local_var_params:
            path_params['subscription_id'] = local_var_params['subscription_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/{subscription_id}',
            method='PUT',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='UpdateSubscriptionResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def update_subscription_source_async(self, request):
        """更新事件订阅源

        更新事件订阅源定义
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for UpdateSubscriptionSource
        :type request: :class:`huaweicloudsdkeg.v1.UpdateSubscriptionSourceRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.UpdateSubscriptionSourceResponse`
        """
        return self._update_subscription_source_with_http_info(request)

    def _update_subscription_source_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in local_var_params:
            path_params['subscription_id'] = local_var_params['subscription_id']
        if 'source_id' in local_var_params:
            path_params['source_id'] = local_var_params['source_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/{subscription_id}/sources/{source_id}',
            method='PUT',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='UpdateSubscriptionSourceResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def update_subscription_target_async(self, request):
        """更新事件订阅目标

        更新事件订阅目标定义
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for UpdateSubscriptionTarget
        :type request: :class:`huaweicloudsdkeg.v1.UpdateSubscriptionTargetRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.UpdateSubscriptionTargetResponse`
        """
        return self._update_subscription_target_with_http_info(request)

    def _update_subscription_target_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}
        if 'subscription_id' in local_var_params:
            path_params['subscription_id'] = local_var_params['subscription_id']
        if 'target_id' in local_var_params:
            path_params['target_id'] = local_var_params['target_id']

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if 'body' in local_var_params:
            body_params = local_var_params['body']
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = ["X-Request-Id", ]

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/{subscription_id}/targets/{target_id}',
            method='PUT',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='UpdateSubscriptionTargetResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_api_versions_async(self, request):
        """获取API版本列表

        获取服务支持的API版本列表
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListApiVersions
        :type request: :class:`huaweicloudsdkeg.v1.ListApiVersionsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListApiVersionsResponse`
        """
        return self._list_api_versions_with_http_info(request)

    def _list_api_versions_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListApiVersionsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def list_obs_buckets_async(self, request):
        """获取obs桶列表

        获取obs桶列表
        
        Please refer to HUAWEI cloud API Explorer for details.


        :param request: Request instance for ListObsBuckets
        :type request: :class:`huaweicloudsdkeg.v1.ListObsBucketsRequest`
        :rtype: :class:`huaweicloudsdkeg.v1.ListObsBucketsResponse`
        """
        return self._list_obs_buckets_with_http_info(request)

    def _list_obs_buckets_with_http_info(self, request):
        local_var_params = {attr: getattr(request, attr) for attr in request.attribute_map if hasattr(request, attr)}

        cname = None

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'offset' in local_var_params:
            query_params.append(('offset', local_var_params['offset']))
        if 'limit' in local_var_params:
            query_params.append(('limit', local_var_params['limit']))
        if 'sort' in local_var_params:
            query_params.append(('sort', local_var_params['sort']))

        header_params = {}

        form_params = {}

        body_params = None
        if isinstance(request, SdkStreamRequest):
            body_params = request.get_file_stream()

        response_headers = []

        header_params['Content-Type'] = http_utils.select_header_content_type(
            ['application/json'])

        auth_settings = []

        return self.call_api(
            resource_path='/v1/{project_id}/subscriptions/obsbuckets',
            method='GET',
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body_params,
            post_params=form_params,
            cname=cname,
            response_type='ListObsBucketsResponse',
            response_headers=response_headers,
            auth_settings=auth_settings,
            collection_formats=collection_formats,
            request_type=request.__class__.__name__)

    def call_api(self, resource_path, method, path_params=None, query_params=None, header_params=None, body=None,
                 post_params=None, cname=None, response_type=None, response_headers=None, auth_settings=None,
                 collection_formats=None, request_type=None):
        """Makes the HTTP request and returns deserialized data.

        :param resource_path: Path to method endpoint.
        :param method: Method to call.
        :param path_params: Path parameters in the url.
        :param query_params: Query parameters in the url.
        :param header_params: Header parameters to be
            placed in the request header.
        :param body: Request body.
        :param post_params: Request post form parameters,
            for `application/x-www-form-urlencoded`, `multipart/form-data`.
        :param cname: Used for obs endpoint.
        :param auth_settings: Auth Settings names for the request.
        :param response_type: Response data type.
        :param response_headers: Header should be added to response data.
        :param collection_formats: dict of collection formats for path, query,
            header, and post parameters.
        :param request_type: Request data type.
        :return:
            Return the response directly.
        """
        return self.do_http_request(
            method=method,
            resource_path=resource_path,
            path_params=path_params,
            query_params=query_params,
            header_params=header_params,
            body=body,
            post_params=post_params,
            cname=cname,
            response_type=response_type,
            response_headers=response_headers,
            collection_formats=collection_formats,
            request_type=request_type,
	    async_request=True)
