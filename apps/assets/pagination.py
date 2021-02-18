from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request

from common.utils import get_logger
from assets.models import Node

logger = get_logger(__name__)


class AssetPaginationBase(LimitOffsetPagination):

    def init_attrs(self, queryset, request: Request, view=None):
        self._request = request
        self._view = view
        self._user = request.user

    def paginate_queryset(self, queryset, request: Request, view=None):
        self.init_attrs(queryset, request, view)
        return super().paginate_queryset(queryset, request, view=None)

    def get_count(self, queryset):
        exclude_query_params = {
            self.limit_query_param,
            self.offset_query_param,
            'key', 'all', 'show_current_asset',
            'cache_policy', 'display', 'draw',
            'order', 'node', 'node_id', 'fields_size',
        }
        for k, v in self._request.query_params.items():
            if k not in exclude_query_params and v is not None:
                logger.warn(f'Not hit node.assets_amount because find a unknow query_param `{k}` -> {self._request.get_full_path()}')
                return super().get_count(queryset)
        node_assets_count = self.get_count_from_nodes(queryset)
        if node_assets_count is None:
            return super().get_count(queryset)
        return node_assets_count

    def get_count_from_nodes(self, queryset):
        raise NotImplementedError


class NodeAssetTreePagination(AssetPaginationBase):
    def get_count_from_nodes(self, queryset):
        is_query_all = self._view.is_query_node_all_assets
        if is_query_all:
            node = self._view.node
            if not node:
                node = Node.org_root()
            logger.debug(f'Hit node.assets_amount[{node.assets_amount}] -> {self._request.get_full_path()}')
            return node.assets_amount
        return None
