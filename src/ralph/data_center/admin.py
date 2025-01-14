# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from ralph.admin import RalphAdmin, RalphTabularInline, register
from ralph.admin.filters import LiquidatedStatusFilter
from ralph.admin.mixins import BulkEditChangeListMixin
from ralph.admin.views.extra import RalphDetailViewAdmin
from ralph.admin.views.multiadd import MulitiAddAdminMixin
from ralph.assets.invoice_report import AssetInvoiceReportMixin
from ralph.assets.models.components import GenericComponent as AssetComponent
from ralph.attachments.admin import AttachmentsMixin
from ralph.data_center.forms.network import NetworkInlineFormset
from ralph.data_center.models.components import DiskShare, DiskShareMount
from ralph.data_center.models.networks import (
    DiscoveryQueue,
    IPAddress,
    Network,
    NetworkEnvironment,
    NetworkKind,
    NetworkTerminator
)
from ralph.data_center.models.physical import (
    Connection,
    DataCenter,
    DataCenterAsset,
    Rack,
    RackAccessory,
    ServerRoom
)
from ralph.data_center.models.virtual import (
    CloudProject,
    Database,
    VIP,
    VirtualServer
)
from ralph.data_center.views.ui import DataCenterAssetSecurityInfo
from ralph.data_importer import resources
from ralph.lib.permissions.admin import PermissionAdminMixin
from ralph.lib.transitions.admin import TransitionAdminMixin
from ralph.licences.models import BaseObjectLicence
from ralph.supports.models import BaseObjectsSupport


@register(DataCenter)
class DataCenterAdmin(RalphAdmin):

    search_fields = ['name']


class NetworkInline(RalphTabularInline):
    formset = NetworkInlineFormset
    model = IPAddress


class NetworkView(RalphDetailViewAdmin):
    icon = 'chain'
    name = 'network'
    label = 'Network'
    url_name = 'network'

    inlines = [NetworkInline]


class DataCenterAssetSupport(RalphDetailViewAdmin):
    icon = 'bookmark'
    name = 'dc_asset_support'
    label = _('Supports')
    url_name = 'data_center_asset_support'

    class DataCenterAssetSupportInline(RalphTabularInline):
        model = BaseObjectsSupport
        raw_id_fields = ('support',)
        extra = 1
        verbose_name = _('Support')
        ordering = ['-support__date_to']

    inlines = [DataCenterAssetSupportInline]


class DataCenterAssetLicence(RalphDetailViewAdmin):
    icon = 'key'
    name = 'dc_asset_licences'
    label = _('Licences')
    url_name = 'data_center_asset_licences'

    class DataCenterAssetLicenceInline(RalphTabularInline):
        model = BaseObjectLicence
        raw_id_fields = ('licence',)
        extra = 1

    inlines = [DataCenterAssetLicenceInline]


class DataCenterAssetComponents(RalphDetailViewAdmin):
    icon = 'folder'
    name = 'dc_components'
    label = _('Components')
    url_name = 'datacenter_asset_components'

    class DataCenterComponentsInline(RalphTabularInline):
        model = AssetComponent
        raw_id_fields = ('model',)
        extra = 1

    inlines = [DataCenterComponentsInline]


@register(DataCenterAsset)
class DataCenterAssetAdmin(
    MulitiAddAdminMixin,
    TransitionAdminMixin,
    BulkEditChangeListMixin,
    PermissionAdminMixin,
    AttachmentsMixin,
    AssetInvoiceReportMixin,
    RalphAdmin,
):
    """Data Center Asset admin class."""
    actions = ['bulk_edit_action']
    change_views = [
        DataCenterAssetComponents,
        DataCenterAssetSecurityInfo,
        DataCenterAssetLicence,
        DataCenterAssetSupport,
        NetworkView,
    ]
    resource_class = resources.DataCenterAssetResource
    list_display = [
        'status', 'barcode', 'model', 'sn', 'hostname', 'invoice_date',
        'invoice_no',
    ]
    multiadd_info_fields = list_display + ['rack']
    one_of_mulitvalue_required = ['sn', 'barcode']
    bulk_edit_list = list_display + [
        'rack', 'orientation', 'position',
        'slot_no', 'price', 'provider'
    ]
    bulk_edit_no_fillable = ['barcode', 'sn']
    search_fields = ['barcode', 'sn', 'hostname', 'invoice_no', 'order_no']
    list_filter = [
        'status', 'barcode', 'sn', 'hostname', 'invoice_no', 'invoice_date',
        'order_no', 'model__name', 'service_env', 'depreciation_end_date',
        'force_depreciation', 'remarks', 'budget_info', 'rack__name',
        'rack__server_room', 'rack__server_room__data_center',
        'property_of', LiquidatedStatusFilter
    ]
    date_hierarchy = 'created'
    list_select_related = ['model', 'model__manufacturer', 'model__category']
    raw_id_fields = ['model', 'rack', 'service_env', 'parent', 'budget_info']
    raw_id_override_parent = {'parent': DataCenterAsset}
    _invoice_report_name = 'invoice-data-center-asset'
    multiadd_clear_fields = [
        {'field': 'management_ip', 'value': None},
        {'field': 'management_hostname', 'value': None},
    ]

    fieldsets = (
        (_('Basic info'), {
            'fields': (
                'hostname', 'model', 'status', 'barcode', 'sn', 'niw',
                'required_support', 'remarks', 'parent', 'tags', 'property_of'
            )
        }),
        (_('Location Info'), {
            'fields': (
                'rack', 'position', 'orientation', 'slot_no',
                'management_ip', 'management_hostname',
            )
        }),
        (_('Usage info'), {
            'fields': (
                'service_env', 'production_year',
                'production_use_date',
            )
        }),
        (_('Financial & Order Info'), {
            'fields': (
                'order_no', 'invoice_date', 'invoice_no', 'task_url', 'price',
                'depreciation_rate', 'depreciation_end_date',
                'force_depreciation', 'source', 'provider', 'delivery_date',
                'budget_info',
            )
        }),
    )

    def get_multiadd_fields(self, obj=None):
        multiadd_fields = [
            {'field': 'sn', 'allow_duplicates': False},
            {'field': 'barcode', 'allow_duplicates': False},
        ]
        return getattr(
            settings, 'MULTIADD_DATA_CENTER_ASSET_FIELDS', None
        ) or multiadd_fields


@register(ServerRoom)
class ServerRoomAdmin(RalphAdmin):

    list_select_related = ['data_center']
    search_fields = ['name', 'data_center__name']
    resource_class = resources.ServerRoomResource
    list_display = ['name', 'data_center']


class RackAccessoryInline(RalphTabularInline):
    model = RackAccessory


@register(Rack)
class RackAdmin(RalphAdmin):

    exclude = ['accessories']
    list_display = ['name', 'server_room_name', 'data_center_name']
    list_filter = ['server_room__data_center']  # TODO use fk field in filter
    list_select_related = ['server_room', 'server_room__data_center']
    search_fields = ['name']
    inlines = [RackAccessoryInline]
    resource_class = resources.RackResource

    def server_room_name(self, obj):
        return obj.server_room.name if obj.server_room else ''
    server_room_name.short_description = _('Server room')
    server_room_name.admin_order_field = 'server_room__name'

    def data_center_name(self, obj):
        return obj.server_room.data_center.name if obj.server_room else ''
    data_center_name.short_description = _('Data Center')
    data_center_name.admin_order_field = 'server_room__data_center__name'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "server_room":
            kwargs["queryset"] = ServerRoom.objects.select_related(
                'data_center',
            )
        return super(RackAdmin, self).formfield_for_foreignkey(
            db_field, request, **kwargs
        )


@register(RackAccessory)
class RackAccessoryAdmin(RalphAdmin):

    list_select_related = ['rack', 'accessory']
    search_fields = ['accessory__name', 'rack__name']
    raw_id_fields = ['rack']
    list_display = ['__str__', 'position']
    resource_class = resources.RackAccessoryResource


@register(Database)
class DatabaseAdmin(RalphAdmin):
    pass


@register(VIP)
class VIPAdmin(RalphAdmin):
    pass


@register(VirtualServer)
class VirtualServerAdmin(RalphAdmin):
    pass


@register(CloudProject)
class CloudProjectAdmin(RalphAdmin):
    pass


@register(Connection)
class ConnectionAdmin(RalphAdmin):

    resource_class = resources.ConnectionResource


@register(DiskShare)
class DiskShareAdmin(RalphAdmin):
    pass


@register(DiskShareMount)
class DiskShareMountAdmin(RalphAdmin):
    pass


@register(Network)
class NetworkAdmin(RalphAdmin):

    resource_class = resources.NetworkResource


@register(NetworkEnvironment)
class NetworkEnvironmentAdmin(RalphAdmin):
    pass


@register(NetworkKind)
class NetworkKindAdmin(RalphAdmin):
    pass


@register(NetworkTerminator)
class NetworkTerminatorAdmin(RalphAdmin):
    pass


@register(DiscoveryQueue)
class DiscoveryQueueAdmin(RalphAdmin):
    pass


@register(IPAddress)
class IPAddressAdmin(RalphAdmin):

    search_fields = ['address']
    list_filter = ['is_public', 'is_management']
    list_display = ['address', 'base_object', 'is_public']
    list_select_related = ['base_object']
    raw_id_fields = ['base_object']
    resource_class = resources.IPAddressResource
