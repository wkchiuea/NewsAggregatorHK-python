configs = [
    {
        "name": "sina",
        "name_zh": "新浪香港",
        "name_en": "sina-hk",
        "base_url": "https://portal.sina.com.hk/",
        "language": "zh",
        "target_categories": ["category/news-hongkong/"],
        # "target_categories": ["category/news-hongkong/", "category/news-china/", "category/news-intl/", "category/finance/"],
        "categories": ["hongkong", "china", "intl", "finance"],
        "news_card_identifier": "article,single-article",
        "headline_identifier": "h1.entry-title",
        "datetime_identifier": "time.entry-date",
        "content_identifier": "div.entry-content",
        "is_debug": True
    },
    {
        "name": "hket",
        "name_zh": "香港經濟日報",
        "name_en": "Hong Kong Economics Times",
        "base_url": "https://inews.hket.com/",
        "language": "zh",
        "target_categories": ["sran009/即市財經", "sran011/國際"],
        "categories": ["finance", "intl"],
        "news_card_identifier": "div.template_item",
        "headline_identifier": "h1",
        "datetime_identifier": "div.date-time",
        "content_identifier": "div.article-detail div.article-detail-body-container",
        "is_debug": True
    },
    {
        "name": "hk01",
        "name_zh": "香港01",
        "name_en": "HK01",
        "base_url": "https://www.hk01.com/",
        "language": "zh",
        "target_categories": ["channel/421/天氣", "channel/2/社會新聞", "channel/364/即時中國", "channel/19/即時國際", "channel/396/財經快訊"],
        "categories": ["weather", "hongkong", "china", "intl", "finance"],
        "news_card_identifier": "div.content-card__main",
        "headline_identifier": "#articleTitle",
        "datetime_identifier": "time",
        "content_identifier": "div.article-grid__content-section",
        "is_debug": True
    },
    {
        "name": "std",
        "name_zh": "星島日報",
        "name_en": "Sing Tao",
        "base_url": "https://std.stheadline.com/",
        "language": "zh",
        "target_categories": ["realtime/hongkong/即時-港聞", "realtime/international/即時-國際", "realtime/china/即時-中國", "realtime/finance/即時-財經"],
        "categories": ["hongkong", "intl", "china", "finance"],
        "news_card_identifier": "div.media.heading-4",
        "headline_identifier": "h1",
        "datetime_identifier": "article.content span.date",
        "content_identifier": "section",
        "is_debug": True
    },
    {
        "name": "stheadline",
        "name_zh": "星島頭條",
        "name_en": "Sing Tao Headline",
        "base_url": "https://www.stheadline.com/",
        "language": "zh",
        "target_categories": ["news/港聞", "china/中國", "world/國際", "finance/財經"],
        "categories": ["hongkong", "china", "intl", "finance"],
        "news_card_identifier": "div.news-detail",
        "headline_identifier": "div.article-title h1",
        "datetime_identifier": "div.time span",
        "content_identifier": "article",
        "is_debug": True
    },
    {
        "name": "mingpao",
        "name_zh": "明報",
        "name_en": "Ming Pao",
        "base_url": "https://news.mingpao.com/",
        "language": "zh",
        "target_categories": ["ins/港聞/section/20240412/s00001", "ins/兩岸/section/20240412/s00004", "ins/國際/section/20240412/s00005"],
        "categories": ["hongkong", "china", "intl"],
        "news_card_identifier": "div.contentwrapper",
        "headline_identifier": "h1",
        "datetime_identifier": "span.time",
        "content_identifier": "article",
        "is_debug": True
    },
    {
        "name": "am730",
        "name_zh": "am730",
        "name_en": "am730",
        "base_url": "https://www.am730.com.hk/",
        "language": "zh",
        "target_categories": ["本地", "國際", "中國", "財經"],
        "categories": ["hongkong", "intl", "china", "finance"],
        "news_card_identifier": "div.newsitem",
        "headline_identifier": "h1.article__head-title",
        "datetime_identifier": "div.article__head-time",
        "content_identifier": "div.article__body",
        "is_debug": True
    },
    {
        "name": "oncc",
        "name_zh": "東方日報",
        "name_en": "Oriental Daily News",
        "base_url": "https://hk.on.cc/",
        "language": "zh",
        "target_categories": ["hk/news/index.html", "hk/cnnews/index.html", "hk/intnews/index.html", "hk/finance/index.html"],
        "categories": ["hongkong", "china", "intl", "finance"],
        "news_card_identifier": "div.focusItem",
        "headline_identifier": "div.topHeadline",
        "datetime_identifier": "span.datetime",
        "content_identifier": "div.breakingNewsContent",
        "is_debug": True
    },
    {
        "name": "now",
        "name_zh": "Now 新聞",
        "name_en": "Now News",
        "base_url": "https://news.now.com/",
        "language": "zh",
        "target_categories": ["home/local", "home/international", "home/finance"],
        "categories": ["hongkong", "intl", "finance"],
        "news_card_identifier": "a.newsWrap",
        "headline_identifier": "h1.newsTitle",
        "datetime_identifier": "time.published",
        "content_identifier": "div.newsLeading",
        "is_debug": True
    },
    {
        "name": "hkej",
        "name_zh": "信報",
        "name_en": "Hong Kong Economic Journal",
        "base_url": "http://www2.hkej.com/",
        "language": "zh",
        "target_categories": ["instantnews/hongkong", "instantnews/china", "instantnews/international"],
        "categories": ["hongkong", "china", "intl"],
        "news_card_identifier": "div.hkej_toc_listingAll_news2_2014",
        "headline_identifier": "#article-title",
        "datetime_identifier": "span.date",
        "content_identifier": "#article-content",
        "is_debug": True
    },
    {
        "name": "tvb",
        "name_zh": "無線新聞",
        "name_en": "TVB News",
        "base_url": "https://news.tvb.com/",
        "language": "zh",
        "target_categories": ["tc/local", "tc/greaterchina", "tc/world", "tc/finance"],
        "categories": ["hongkong", "china", "intl", "finance"],
        "news_card_identifier": "div.BigNewsContainer",
        "headline_identifier": "h1",
        "datetime_identifier": "div.entryCateInfo",
        "content_identifier": "h6.descContainer",
        "is_debug": True
    },
    {
        "name": "rthk-zh",
        "name_zh": "香港電台中文新聞",
        "name_en": "RTHK Chinese News",
        "base_url": "https://news.rthk.hk/",
        "language": "zh",
        "target_categories": ["rthk/ch/latest-news/local.htm", "rthk/ch/latest-news/greater-china.htm", "rthk/ch/latest-news/world-news.htm", "rthk/ch/latest-news/finance.htm"],
        "categories": ["hongkong", "china", "intl", "finance"],
        "news_card_identifier": "div.ns2-page",
        "headline_identifier": "h2.itemTitle",
        "datetime_identifier": "div.createddate",
        "content_identifier": "div.itemBody",
        "is_debug": True
    },
    {
        "name": "rthk-en",
        "name_zh": "香港電台英文新聞",
        "name_en": "RTHK English News",
        "base_url": "https://news.rthk.hk/",
        "language": "en",
        "target_categories": ["rthk/en/latest-news/local.htm", "rthk/en/latest-news/greater-china.htm", "rthk/en/latest-news/world-news.htm", "rthk/en/latest-news/finance.htm"],
        "categories": ["hongkong", "china", "intl", "finance"],
        "news_card_identifier": "div.ns2-page",
        "headline_identifier": "h2.itemTitle",
        "datetime_identifier": "div.createddate",
        "content_identifier": "div.itemBody",
        "is_debug": True
    },
    {
        "name": "scmp",
        "name_zh": "南華早報",
        "name_en": "South China Morning Post",
        "base_url": "https://www.scmp.com/",
        "language": "en",
        "target_categories": ["news/hong-kong", "news/china", "economy", "news/world"],
        "categories": ["hongkong", "china", "finance", "intl"],
        "news_card_identifier": 'div[data-qa=\"Component-Container\"] a[href*=\"article\"]',
        "headline_identifier": 'h2[data-qa=\"ContentHeadline-Container\"]',
        "datetime_identifier": 'time[data-qa=\"DefaultArticleDate-time\"]',
        "content_identifier": 'div[data-qa=\"GenericArticle-Content\"]',
        "is_debug": True
    },
    {
        "name": "wenweipo",
        "name_zh": "文匯報",
        "name_en": "Wen Wei Po",
        "base_url": "https://www.wenweipo.com/",
        "language": "zh",
        "target_categories": ["immed/hongkong", "immed/inland", "immed/world"],
        "categories": ["hongkong", "china", "intl"],
        "news_card_identifier": "div.story-item",
        "headline_identifier": "h1",
        "datetime_identifier": "time.publish-date",
        "content_identifier": "div.post-body",
        "is_debug": True
    },
    {
        "name": "takungpao",
        "name_zh": "大公報",
        "name_en": "Ta Kung Pao",
        "base_url": "http://www.takungpao.com.hk/",
        "language": "zh",
        "target_categories": ["hongkong/", "mainland/", "international/", "finance/"],
        "categories": ["hongkong", "china", "intl", "finance"],
        "news_card_identifier": "div.content",
        "headline_identifier": "h1.tkp_con_title",
        "datetime_identifier": "h2.tkp_con_author",
        "content_identifier": "div.tkp_content",
        "is_debug": True
    }
]
