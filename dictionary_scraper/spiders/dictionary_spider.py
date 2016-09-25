import scrapy

class Parsers(object):

    def __init__(self, parser, url):
        self._parser = parser
        self._url = url

    @property
    def url(self):
        ''' Get the current url '''
        return  self._url

    @property
    def parser(self):
        ''' Get the current parser '''
        return self._parser

class DictionarySpider(scrapy.Spider):
    name = "dictionary"
    word_lists = ['embark','factual']
    
    def __init__(self,*args, **kwargs):
        super(DictionarySpider,self).__init__(*args, **kwargs)
        self.url_parsers =[
            Parsers(self.parse, 'http://www.yourdictionary.com/%s'),
            Parsers(self.parse_sentence, 'http://sentence.yourdictionary.com/%s')
        ]

    def start_requests(self):
        for parser in self.url_parsers:
            for word in self.word_lists:
                word_url = parser.url%(word)
                yield scrapy.Request(url=word_url, callback=parser.parser)

        
    def parse(self, response):
        sentenceBullets = response.xpath("//*[contains(@class,'examplesBox')]//*[@class='greybullets']/li/span")
        texts = []
        for sentence in sentenceBullets:
            text = sentence.xpath('.//text()').extract()
            texts.append(''.join(text))
            
        yield{
            'sentences': texts,
            'reference': 'yourdictionary.com'
        }

    def parse_sentence(self, response):
        sentenceBullets = response.xpath("//*[@class='li_content']")
        texts = []
        for sentence in sentenceBullets:
            text = sentence.xpath('.//text()').extract()
            texts.append(''.join(text))
            
        yield{
            'sentences': texts,
            'reference': 'sentence.yourdictionary.com'
        }        
