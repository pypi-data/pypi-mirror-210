from haystack import indexes

from .models import Transact


class TransactIndex(indexes.SearchIndex, indexes.Indexable):
    """
    Transact索引数据模型类
    """
    text = indexes.CharField(document=True, use_template=True)
    # 以下是为了在使用时 news.id 如果没有写就需要news.object.id
    id = indexes.IntegerField(model_attr='id')
    summary = indexes.CharField(model_attr='summary')

    def get_model(self):
        """返回建立索引的模型类"""
        return Transact

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)
