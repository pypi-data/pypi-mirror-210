import unittest,simplejson,sys
from InCli.SFAPI import restClient,query,Sobjects,utils,jsonFile,file_csv


class Test_Objects(unittest.TestCase):

    def test_objects(self):
        restClient.init('NOSQSM')
        
        res = Sobjects.get_with_only_id('a3m3O000000KCjCQAW')

        print()     
    def test_limits(self):
        restClient.init('DEVNOSCAT2')
        action = '/services/data/v51.0/limits'
        res = restClient.callAPI(action)

        print()


    def test_id(self):
        restClient.init('DEVNOSCAT2')
        action = '/services/data/v51.0'
        res = restClient.callAPI(action)

        print()

    def test_id(self):
        restClient.init('DEVNOSCAT2')
        action = '/services/data/v51.0'
        res = restClient.callAPI(action)
        for key in res.keys():
            print()
            action = res[key]
            res1 = restClient.callAPI(action)
            print(action)
            print(res1)

        print()

    def getAttributes(self,product):
        attr_str = product['vlocity_cmt__AttributeMetadata__c']
        if attr_str == None: return None
        atributes = simplejson.loads(attr_str)

        atts = []
        for atribute in atributes['records']:
            for productAttribute in atribute['productAttributes']['records']:
                if 'values' not in productAttribute:
                    a=1
                if productAttribute['values'] == None:
                    a=1
                att = {
                    'att':atribute['Code__c'],
                    'pAtt':productAttribute['code'],
                    'type':productAttribute['inputType'],
                    'len':len(productAttribute['values']) if 'values' in productAttribute and productAttribute['values'] != None else 0
                }

                atts.append(att)
        return atts

    def getChildProducts(self,product):
        children = []
        childItems = query.queryRecords(f"select fields(all) from vlocity_cmt__ProductChildItem__c where vlocity_cmt__ParentProductId__c='{product['Id']}' and vlocity_cmt__IsOverride__c = False limit 200")
        if len(childItems) == 0:
            return []

        for childItem in childItems:
            if childItem['vlocity_cmt__ChildProductId__c'] == None:
                continue
            prod = Sobjects.getF('Product2',f"Id:{childItem['vlocity_cmt__ChildProductId__c']}")['records'][0]
            print(prod['Name'])

            child = {
                'Name':childItem['vlocity_cmt__ChildProductName__c'],
                'virtual':childItem['vlocity_cmt__IsVirtualItem__c'],
                'Id':childItem['vlocity_cmt__ChildProductId__c'],
                'attributes':self.getAttributes(prod),
                'children':self.getChildProducts(prod),
                'mmq':f"({childItem['vlocity_cmt__MinMaxDefaultQty__c']})".replace(' ',''),
                "child_mm":f"[{int(childItem['vlocity_cmt__MinimumChildItemQuantity__c'])},{int(childItem['vlocity_cmt__MaximumChildItemQuantity__c'])}]"
            }
            children.append(child)
            print(childItem['vlocity_cmt__ChildProductName__c'])

        return children

    code = 'PROMO_NOS_OFFER_005'

    def test_getF(self):
        restClient.init('NOSDEV')

        res = Sobjects.getF('Product2',"ProductCode:C_NOS_OFFER_001")

        code='PROMO_WOO_FIXED_INTERNET_MOBILE_12_MONTHS_008'
        promo = Sobjects.getF('vlocity_cmt__Promotion__c',f"vlocity_cmt__Code__c:{self.code}")

        promoItems = query.queryRecords(f"select fields(all) from vlocity_cmt__PromotionItem__c where vlocity_cmt__PromotionId__c='{promo['records'][0]['Id']}' limit 200")
        root = {
            'children':[],
            'Name':'root',
            'Id':'NA',
            'attributes':"NA"
        }
        for promoItem in promoItems:
            prods = Sobjects.getF('Product2',f"Id:{promoItem['vlocity_cmt__ProductId__c']}")

            for prod in prods['records']:
                _product = {
                    'Name':prod['Name'],
                    'virtual':False,
                    'Id':prod['Id'],
                    'attributes':self.getAttributes(prod),
                    'children':self.getChildProducts(prod),
                    'mmq':"",
                    'child_mm':""
                }
                root['children'].append(_product)
        jsonFile.write(f'prod123_{self.code}',root)

        self.printProduct(root)

    def test_print_from_file(self):
        root = jsonFile.read(f'prod123_{self.code}')
        self.printProduct(root)


    def get_product_decomposition(self,product):
        q = f"select fields(all) from vlocity_cmt__DecompositionRelationship__c where vlocity_cmt__SourceProductId__c='{product['Id']}' limit 200"
        res = query.query(q)
        product['decompositions'] = []
        for record in res['records']:
            mappring_data_str = record['vlocity_cmt__MappingsData__c']
            mappring_data = simplejson.loads(mappring_data_str) if mappring_data_str != None else None

            mappings =[]
            if mappring_data != None:
                for mapping in mappring_data:
                    if mapping['mapping_type'] == 'ad-verbatim':
                        if mapping['source_type'] == 'Attribute':
                            mappings.append({
                                'from':mapping['source_attr_code'],
                                'to':mapping['destination_attr_code']
                            })
                        elif mapping['source_type'] == 'Field':
                            mappings.append({
                                'from':mapping['source_field_name'],
                                'to':mapping['destination_attr_code']
                            })
                        else:
                            a=1
                    elif mapping['mapping_type'] == 'static':
                        mappings.append({
                            'from':'Static',
                            'to':mapping['destination_attr_code']
                        })

                    elif mapping['mapping_type'] == 'list':
                        if mapping['source_type'] == 'Attribute':
                            mappings.append({
                                'from':mapping['source_attr_code'],
                                'to':mapping['destination_attr_code']
                            })
                        elif mapping['source_type'] == 'Field':
                            mappings.append({
                                'from':mapping['source_field_name'],
                                'to':mapping['destination_attr_code']
                            })
                        else:
                            a=1
                    else:
                        a=1

            condition_data_str = record['vlocity_cmt__ConditionData__c']
            condition_data = simplejson.loads(condition_data_str) if condition_data_str!=None else None

            decomposition = {
                'conditions' :len(condition_data['singleconditions']) if condition_data != None else 0,
                'mapping_rules':len(mappring_data) if mappring_data != None else 0,
                'Name':record['Name'],
                'destination_Id':record['vlocity_cmt__DestinationProductId__c'],
                'mappings':mappings
            }
            product['decompositions'].append(decomposition)

            if decomposition['destination_Id'] != None:

                q = f"select fields(all) from vlocity_cmt__DecompositionRelationship__c where vlocity_cmt__SourceProductId__c='{decomposition['destination_Id']}' limit 200"
                res = query.query(q)
                if len(res['records'])>0:
                    level = 2 if 'level' not in product else product['level']+1
                    if 'level' in product:
                        a=1
                    fake_product = {
                        'Id':decomposition['destination_Id'],
                        'level':level
                    }
                    self.get_product_decomposition(fake_product)
                    decomposition['next_level'] = fake_product['decompositions']
                    print()
            else:
                a=1

            print(record['Name'])

        print()

    def test_decomposition_rules(self):
        restClient.init('NOSDEV')

        root = jsonFile.read(f'prod123_{self.code}')

        def get_decomposition(product):
            self.get_product_decomposition(product)
            for child in product['children']:
                get_decomposition(child)

        for children in root['children']:
            get_decomposition(children)

        jsonFile.write(f'prod123_decomposed_{self.code}',root)


        print()

    def flatten(self,product):
        a=1




    def printProduct(self,products,path=[]):

        filename = f'prod123_decomposed_{self.code}_csv.csv'
        original_stdout = sys.stdout

        with open(filename, 'w') as f:
            sys.stdout = f 

            def printProduct_inner(products,path=[]):
                if products == None:
                    a=1
                for product in products['children']:
                    spath = path.copy()
                    spath.append(f"{product['Name']}{product['mmq']}{product['child_mm']}")

                    self.printAttribute(spath,product['attributes'])
                    self.print_decomposition(spath,product['decompositions'])
                    try:
                        printProduct_inner(product,spath)
                    except Exception as e:
                        print(e)
            printProduct_inner(products)
        sys.stdout = original_stdout 

        print()


    def printAttribute(self,path,attributes):
        spath = path.copy()
        while len(spath)<5:
            spath.append("")

        _path = ";".join(spath)

        if attributes == None: 
     #       print(f"{_path}")
            return
        for atttribute in attributes:
            print(f"{_path};{atttribute['att']}-{atttribute['pAtt']};{atttribute['type']};{atttribute['len']}")


    def print_decomposition(self,path,decompostions):
        spath = path.copy()
        while len(spath)<8:
            spath.append("")

        _path = ";".join(spath)

        if decompostions == None: 
     #       print(f"{_path}")
            return

        def print_next_level(path,next_decompositions,level):
            for next_decomposition in next_decompositions:
                xx = []
                while len(xx)< (3 + (level-1)):
                    xx.append("")
                spaces = ";".join(xx)
                for next_mapping in next_decomposition['mappings']:
                    print(f"{path};{spaces};{next_decomposition['Name']};{next_mapping['from']}->{next_mapping['to']}")
                if 'next_level' in next_decomposition:
                    print_next_level(f"{_path};{decomposition['Name']};{next_decomposition['Name']}",next_decomposition['next_level'],level+1)

        for decomposition in decompostions:
            for mapping in decomposition['mappings']:
                print(f"{_path};{decomposition['Name']};{decomposition['conditions']};{decomposition['mapping_rules']};{mapping['from']}->{mapping['to']}")
            if 'next_level' in decomposition:
                print_next_level(f"{_path};{decomposition['Name']}",decomposition['next_level'],1)

    def test_print_from_file_deco(self):
        root = jsonFile.read(f'prod123_decomposed_{self.code}')
        self.printProduct(root)

#####################################################################
    def printProduct2(self,products,path=[]):

        filename = f'prod123_decomposed2_{self.code}_csv.csv'
        original_stdout = sys.stdout

        with open(filename, 'w') as f:
            sys.stdout = f 

            def printProduct_inner(products,path=[]):
                if products == None:
                    a=1
                for product in products['children']:
                    spath = path.copy()
                    virtual = " VIRTUAL " if product['virtual'] == True else ""
                    spath.append(f"{virtual}{product['Name']}{product['mmq']}{product['child_mm']}")

                    self.printAttribute2(spath,product['attributes'])
                    self.print_decomposition2(spath,product['decompositions'])
                    try:
                        printProduct_inner(product,spath)
                    except Exception as e:
                        print(e)
            printProduct_inner(products)
        sys.stdout = original_stdout 

        print()


    def printAttribute2(self,path,attributes):
        spath = path.copy()
        while len(spath)<5:
            spath.append("")

        _path = ";".join(spath)

        if attributes == None: 
     #       print(f"{_path}")
            return
        for atttribute in attributes:
            att = f"{atttribute['att']}-{atttribute['pAtt']}"
            print(f"{_path};AT:  {att};AT:{atttribute['type']} {atttribute['len']}")


    def print_decomposition2(self,path,decompostions):
        spath = path.copy()
        while len(spath)<5:
            spath.append("")

        _path = ";".join(spath)

        if decompostions == None: 
     #       print(f"{_path}")
            return

        def print_next_level(path,next_decompositions,level):
            for next_decomposition in next_decompositions:
                xx = []
                while len(xx)< (3 + (level-1)):
                    xx.append("")
                spaces = ";".join(xx)
                spaces = ''
                for next_mapping in next_decomposition['mappings']:
                    print(f"{path};DE: {next_decomposition['Name']};MAP: {next_mapping['from']}->{next_mapping['to']}")
                if 'next_level' in next_decomposition:
                    print_next_level(f"{_path};DE: {decomposition['Name']};DE: {next_decomposition['Name']}",next_decomposition['next_level'],level+1)

        for decomposition in decompostions:
            for mapping in decomposition['mappings']:
                print(f"{_path};DE: {decomposition['Name']}  C:{decomposition['conditions']};MAP: {mapping['from']}->{mapping['to']}")
            if 'next_level' in decomposition:
                print_next_level(f"{_path};DE: {decomposition['Name']}  C:{decomposition['conditions']}",decomposition['next_level'],1)

    def test_print_from_file_deco2(self):
        root = jsonFile.read(f'prod123_decomposed_{self.code}')
        self.printProduct2(root)