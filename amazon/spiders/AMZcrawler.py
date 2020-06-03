# -*- coding: utf-8 -*-
import scrapy
import logging
counter = 0

'''Search Parameter'''
search_item = 'ergonomic office chair' # Change this string to whatever you are searching

class SpirulinaSpider(scrapy.Spider):
    name = 'spirulina' # This is the spider name - affectionally called by the item that inspired me to create spiders
    allowed_domains = ['www.amazon.com']
    

    def start_requests(self):
        global search_item
        urlvariable = 'https://www.amazon.com/s?k='+search_item
        yield scrapy.Request(url=urlvariable, callback=self.parse, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
        })

    '''Parses through the main search result page items'''
    def parse(self, response):
        global counter       
        products = response.xpath("//div[@class='s-main-slot s-result-list s-search-results sg-row']//div[@data-asin!='' and @data-index]")

        '''Gets link for each product'''
        for product in products:

            deep_url = product.xpath(".//h2/a/@href").get()
            yield response.follow(url=deep_url, callback = self.parse_deep, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            })

        '''Gets link for next page'''
        next_page = response.urljoin(response.xpath(
            "//ul[@class='a-pagination']/li[position() = last()]/a/@href").get())
        
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
            })

    '''Gets information from each product'''
    def parse_deep(self, response):

        #Gather Generic Data
        product_asin = response.xpath("//div[@id='cerberus-data-metrics']/@data-asin").get()
        product_name = response.xpath("normalize-space(//span[@id='productTitle']/text())").get()
        product_seller = response.xpath("//a[@id='bylineInfo']/text()").get()
        product_price = response.xpath("//div[@id='cerberus-data-metrics']/@data-asin-price").get()
        product_sale_price = response.xpath("//span[@id='priceblock_pospromoprice']/text()").get()
        amazon_coupon = response.xpath("normalize-space(//div[@id='clippedCoupon']//div/div/span/text())").get()
        product_unit_price = response.xpath("//div[@id='price']//span[@class='a-size-small a-color-price']/text()").get()
        product_size = response.xpath("normalize-space(//span[@class='selection']/text())").get()
        product_star_rating = response.xpath("//span[@data-hook='rating-out-of-text']/text()").get()
        product_num_reviews = response.xpath("//span[@id='acrCustomerReviewText']/text()").get()
        product_customer_5_star = response.xpath("normalize-space(//table[@id='histogramTable']//tr[1]//div[@class='a-meter']/@aria-label)").get()
        product_customer_4_star = response.xpath("normalize-space(//table[@id='histogramTable']//tr[2]//div[@class='a-meter']/@aria-label)").get()
        product_customer_3_star = response.xpath("normalize-space(//table[@id='histogramTable']//tr[3]//div[@class='a-meter']/@aria-label)").get()
        product_customer_2_star = response.xpath("normalize-space(//table[@id='histogramTable']//tr[4]//div[@class='a-meter']/@aria-label)").get()
        product_customer_1_star = response.xpath("normalize-space(//table[@id='histogramTable']//tr[5]//div[@class='a-meter']/@aria-label)").get()


        #Morph Data into readable format
        product_star_rating = self.format_stars(product_star_rating)
        product_num_reviews = self.format_ratings(product_num_reviews)
        product_unit_price = self.format_unit_price(product_unit_price)
        product_sale_price = self.format_price(product_sale_price)
        product_price = self.format_price(product_price)

        #Built Data - Data built from other data
        product_url = self.hyperlink_creator(product_asin)

        #Return Results
        yield{
            "Product ASIN": product_asin,
            "Product Name": product_name,
            "Product URL": product_url,
            "Product Seller": product_seller,
            "Product Price": product_price,
            "Product Sale Price": product_sale_price,
            "Amazon Coupon": amazon_coupon,
            "Product Unit Price": product_unit_price,
            "Product Size": product_size,
            "Product Star Rating": product_star_rating,
            "Product Number Reviews" :product_num_reviews,
            "5-Star Rating": product_customer_5_star,
            "4-Star Rating": product_customer_4_star,
            "3-Star Rating": product_customer_3_star,
            "2-Star Rating": product_customer_2_star,
            "1-Star Rating": product_customer_1_star
        }

    def format_price(self, price):
        '''Converts price to a regular number'''
        try:
            return float(price.replace('$',''))
        except:
            return price

    def format_stars(self, star_rating):
        '''Removes " out of 5 stars" from title'''
        try:
            return float(star_rating.replace(' out of 5',''))
        except:
            return star_rating

    def format_ratings(self, ratings):
        '''Removes commas, "ratings", and changes string to float'''
        try:
            return int(ratings.replace(',','').replace('rating','').replace('s',""))
        except:
            return ratings

    def hyperlink_creator(self,product_asin):
        '''creates URL from ASIN'''
        try:
            return "https://www.amazon.com/dp/"+product_asin
        except:
            pass

    def format_unit_price(self,unit_price):
        '''Removes parentheses'''
        try:
            return unit_price.replace("(","").replace(")","")
        except:
            return unit_price
