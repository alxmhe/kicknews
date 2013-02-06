import datetime
from haystack import indexes
from opennews.models import Article, Tag, Category

class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    tags = indexes.CharField()

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()

    def prepare(self, object):
		self.prepared_data = super(ArticleIndex, self).prepare(object)

		self.prepared_data['tags'] = [tag.tag for tag in object.tags.all()]

		return self.prepared_data