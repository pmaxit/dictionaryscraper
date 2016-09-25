import scrapy
from dictionary_scraper.items import DictionaryScraperItem

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

        self.callstack  = [
            Parsers(self.parse_sentence, 'http://sentence.yourdictionary.com/%s'),
            Parsers(self.parse_words, 'http://www.dictionary.com/browse/%s'),
        ]

    def call_next(self,**kwargs):
        ''' call next target for item loder or yields if it is completed '''

        # Get the meta object
        meta = kwargs['meta']

        item = meta['item']
        if(len(meta['callstack']) >0):
            target = meta['callstack'].pop(0)
            yield scrapy.Request(target.url%(item['word']), meta=meta, callback=target.parser, errback=self.call_next)
        else:
            yield meta['item']

    def start_requests(self):
        
        for word in self.word_lists:
            item = DictionaryScraperItem()
            item['word'] = word
            
            meta = {}
            meta['item'] = item
            meta['callstack'] = self.callstack[:]

            # Pick first item from stack
            target = meta['callstack'].pop(0)
            yield scrapy.Request(target.url%(item['word']), meta=meta, callback=target.parser, errback=self.call_next)            


    def parse_sentence(self, response):
        item = response.meta['item']
        sentenceBullets = response.xpath("//*[@class='li_content']")
        sentences = []
        for sentence in sentenceBullets:
            text = sentence.xpath('.//text()').extract()
            sentences.append(''.join(text))
        
        item['sentences'] = sentences
        return self.call_next(meta=response.meta)
    
    def extract(self,elem):
        return ' '.join(elem.extract())

    def parse_words(self, response):
        ''' dictionary parser for dictionary.com'''
        item = response.meta['item']
        deflist = response.xpath("//*[@class='def-list']/section")
        meanings=[]
        for section in deflist[:-1]:
            meaning={}
            meaning['scope'] = self.extract(section.xpath("./header/span//text()"))
            meaning['definition'] = []
            for meaningdivs in section.xpath(".//*[@class='def-set']"):
                text =  self.extract(meaningdivs.xpath(".//*[@class='def-content']//text()"))
                meaning['definition'].append(text)
            
            meanings.append(meaning)

        # Parse origin
        tailelements = response.xpath(".//*[@class='tail-wrapper']//*[@class='tail-elements']")
        originText = ""
        for span in tailelements[0].xpath('./span'):
            originText = originText + self.extract(span.xpath('.//text()'))

        item['meanings'] = meanings

        #Todo: Not good origin statement. Research for good sources.
        item['origin'] = originText

        return self.call_next(meta=response.meta)


