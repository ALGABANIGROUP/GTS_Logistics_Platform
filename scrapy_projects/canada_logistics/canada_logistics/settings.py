import scrapy_poet
import scrapy_zyte_api

BOT_NAME = "canada_logistics"

SPIDER_MODULES = ["canada_logistics.spiders"]
NEWSPIDER_MODULE = "canada_logistics.spiders"

ADDONS = {
    scrapy_poet.Addon: 300,
    scrapy_zyte_api.Addon: 500,
}

SCRAPY_POET_DISCOVER = ["canada_logistics.pages"]

#ZYTE_API_KEY = "YOUR_API_KEY"
ZYTE_API_TRANSPARENT_MODE = False
