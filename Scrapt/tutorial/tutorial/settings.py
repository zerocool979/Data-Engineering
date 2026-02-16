BOT_NAME = 'tutorial'

SPIDER_MODULES = ['tutorial.spiders']
NEWSPIDER_MODULE = 'tutorial.spiders'

ROBOTSTXT_OBEY = False

USER_AGENT = 'Mozilla/5.0'

ITEM_PIPELINES = {
   'tutorial.pipelines.TutorialPipeline': 300,
}

DOWNLOAD_DELAY = 2
