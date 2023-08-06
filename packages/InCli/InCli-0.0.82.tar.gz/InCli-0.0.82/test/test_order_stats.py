import unittest,simplejson,sys
from InCli.SFAPI import restClient,query,Sobjects,utils,jsonFile,file_csv
from collections import Counter


class Test_Order_stats(unittest.TestCase):
    dec_num = 0
    orderId = '8013O000003cE7VQAU'

    def test_order_to_file(self):

        self.orderId='8013O000003jDscQAE'
        text='NOS4u_100'

        filename = f'Decomposition_order_{self.orderId}_{text}.txt'
        original_stdout = sys.stdout
        
        restClient.init('NOSDEV')

        with open(filename, 'w') as f:
            sys.stdout = f 
            self.test_order()

        sys.stdout = original_stdout 

    def get_order_items(self,orderId):
        q = f"select fields(all) from orderitem where OrderId='{orderId}' limit 200"
        order_items = query.query(q)  
        return   order_items

    def get_products_for_order_items(self,order_items):
        product2Ids = [order_item['Product2Id'] for order_item in order_items['records'] ]
        product2Ids_str = query.IN_clause(product2Ids)

        qp = f"select fields(all) from product2 where Id in ({product2Ids_str})"
        product2s = query.query(qp)
        return product2s

    def get_fulfilment_requests(self,orderId):
        q2= f"select fields(all) from vlocity_cmt__FulfilmentRequest__c where vlocity_cmt__OrderId__c = '{self.orderId}' limit 200"
        frs = query.query(q2)
        return frs
    
    def get_frls_for_frs(self,frs):
        fr_ids = [r['Id'] for r in frs['records']]
        fr_ids_str = query.IN_clause(fr_ids)

        q3= f"select fields(all) from vlocity_cmt__FulfilmentRequestLine__c where vlocity_cmt__FulfilmentRequestID__c in ({fr_ids_str}) limit 200"
        frls = query.query(q3)

        return frls

    def get_product2_for_frls(self,frls):
        rfl_product2_ids = [r['vlocity_cmt__Product2Id__c'] for r in frls['records']]
        rfl_product2_ids_str = query.IN_clause(rfl_product2_ids)
        rfl_products_q = f"select fields(all) from product2 where Id in ({rfl_product2_ids_str})"
        rfl_products = query.query(rfl_products_q)
        return rfl_products

    def test_order(self):

        order_items = self.get_order_items(self.orderId)

        print(f"Order line items {len(order_items['records'])}")

        product2s = self.get_products_for_order_items(order_items)

        
        def print_decom(decom):
            print(f"       Decomposition relationship: {decom['Name']:<80}  {decom['source_Id']}->{decom['destination_Id']}  Conditions:{decom['conditions']}  mappings:{decom['mapping_rules']}")
         #   if decom['conditions_str']!=None: print(f"               {decom['conditions_str']}")
            self.dec_num = self.dec_num + 1
            if 'next_level' in decom:
                for dec in decom['next_level']:
                    print_decom(dec)

        for x,order_item in enumerate(order_items['records']):
         #   attr_str = order_item['vlocity_cmt__AttributeSelectedValues__c']
            product = [p2 for p2 in product2s['records'] if p2['Id']==order_item['Product2Id']][0]
            prod_attr_str = product['vlocity_cmt__AttributeMetadata__c']
            attributes = simplejson.loads(prod_attr_str)
            print(f"- Line {x+1} - Product:{product['Name']}  {product['ProductCode']}  Action:{order_item['vlocity_cmt__Action__c']}")
            for attribute in attributes['records']:
                for product_attributes  in attribute['productAttributes']['records']:
                    count = len(product_attributes['values']) if 'values' in product_attributes and product_attributes['inputType']=='dropdown' else 1
                    values = [value['value'] for value in product_attributes['values']] if product_attributes['inputType'] == 'dropdown' else []
                    val = ", ".join(values)
                    print(f"       Attribute {product_attributes['code']:<50}: {product_attributes['inputType']:<10} ({count:>2})  {val}")

            self.get_product_decomposition(product)
            for decom in product['decompositions']:
                print_decom(decom)
           # attr = simplejson.loads(attr_str)
        print()
        print(f"total decomposition relationships {self.dec_num}")
        print()
      #  q2= f"select fields(all) from vlocity_cmt__FulfilmentRequest__c where vlocity_cmt__OrderId__c = '{self.orderId}' limit 200"
        frs = self.get_fulfilment_requests(self.orderId)

        print()
        print(f"Fulfilment Lines {len(frs['records'])}")

        frls = self.get_frls_for_frs(frs)

        rfl_products = self.get_product2_for_frls(frls)

        frls['records'][0]['vlocity_cmt__Product2Id__c']
        for y,fr in enumerate(frs['records']):
            frl_s = [r for r in frls['records'] if r['vlocity_cmt__FulfilmentRequestID__c']==fr['Id']]
            print(f" - FR: Line {y+1} {fr['Name']}  Status:{fr['vlocity_cmt__Status__c']} ")  

            for z,frl in enumerate(frl_s):
                frl_prod = [r for r in rfl_products['records'] if r['Id']==frl['vlocity_cmt__Product2Id__c']][0]
                mu = simplejson.loads(frl['vlocity_cmt__AttributesMarkupData__c'])
                at = simplejson.loads(frl['vlocity_cmt__JSONAttribute__c'])
                print(f"   - FRL: {z+1} {frl['Name']}  Product:{frl_prod['Name']}   Action:{frl['vlocity_cmt__Action__c']}")  

                for frl_att in at.keys():
                    print(f"      {frl_att} {len(at[frl_att])}")  
                    frl_att_as = at[frl_att]
                    for frl_att_a in frl_att_as:
                        count = len(frl_att_a['attributeRunTimeInfo']['values']) if frl_att_a['attributeRunTimeInfo']['dataType'] == 'Picklist' else 1
                        values = [value['value'] for value in frl_att_a['attributeRunTimeInfo']['values']] if frl_att_a['attributeRunTimeInfo']['dataType'] == 'Picklist' else []
                        val = ", ".join(values)

                        print(f"          {frl_att_a['attributeuniquecode__c']:<50}  {frl_att_a['attributeRunTimeInfo']['dataType']:<10}  ({count:>2})     {val}")

        q4 = f"select fields(all) from vlocity_cmt__OrchestrationItem__c where vlocity_cmt__OrchestrationPlanId__c = '{frs['records'][0]['vlocity_cmt__orchestrationPlanId__c']}' limit 200"
        res4 = query.query(q4)
        OrchestrationItemTypes=[]
        for rec4 in res4['records']:
            OrchestrationItemTypes.append(rec4['vlocity_cmt__OrchestrationItemType__c'])

        print()
        print()

        c = Counter(OrchestrationItemTypes)
        print(c)
        print()

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

    def test_parse_product(self):
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

    def parse_conditions(self,condition_data):
        if condition_data == None: 
            return None

        def parse_single_condition(single_condition_a,op):
            conditions =[]

            for sc in single_condition_a:
                if 'singleconditions' in sc:
                    conditions.append(parse_single_condition(sc['singleconditions'],sc['type']))
                else:
                    condition = f"({sc['left-side']} {sc['op']} {sc['right-side']})"
                    conditions.append(condition)
            _op = f" {op} "
            condition =F"({_op.join(conditions)})"  
            return condition     

        all_conditions=[]
        for single_conditions in condition_data['singleconditions']:
            if 'singleconditions' in single_conditions:
                condition = parse_single_condition(single_conditions['singleconditions'],condition_data['type'])
            else:
                condition = f"({single_conditions['left-side']} {single_conditions['op']} {single_conditions['right-side']})"
            all_conditions.append(condition)

        if len(all_conditions)>1:
            op = F" {condition_data['type']} "
            final_condition = F"{op.join(all_conditions)}"
            return final_condition
        else:
            return all_conditions[0]
        return None

    def parse_decomposition_mapping(self,mapping,mappings):
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
 
    def get_product_decomposition(self,product):
        q = f"select fields(all) from vlocity_cmt__DecompositionRelationship__c where vlocity_cmt__SourceProductId__c='{product['Id']}' limit 200"
        decomposition_relationships = query.query(q)
        product['decompositions'] = []
        for decomposition_relationship in decomposition_relationships['records']:
            mappring_data_str = decomposition_relationship['vlocity_cmt__MappingsData__c']
            mappring_data = simplejson.loads(decomposition_relationship['vlocity_cmt__MappingsData__c']) if mappring_data_str != None else None

            mappings =[]
            if mappring_data != None:
                for mapping in mappring_data:
                    self.parse_decomposition_mapping(mapping,mappings)

            condition_data_str = decomposition_relationship['vlocity_cmt__ConditionData__c']
            condition_data = simplejson.loads(condition_data_str) if condition_data_str!=None else None

            self.parse_conditions(condition_data)

            decomposition = {
                'conditions' :len(condition_data['singleconditions']) if condition_data != None else 0,
                'conditions_str':self.parse_conditions(condition_data),
                'mapping_rules':len(mappring_data) if mappring_data != None else 0,
                'Name':decomposition_relationship['Name'],
                'destination_Id':decomposition_relationship['vlocity_cmt__DestinationProductId__c'],
                'source_Id':decomposition_relationship['vlocity_cmt__SourceProductId__c'],
                'mappings':mappings
            }
            product['decompositions'].append(decomposition)

            if decomposition['destination_Id'] != None:
                q = f"select fields(all) from vlocity_cmt__DecompositionRelationship__c where vlocity_cmt__SourceProductId__c='{decomposition['destination_Id']}' limit 200"
                res2 = query.query(q)
                if len(res2['records'])>0:
                    level = 2 if 'level' not in product else product['level']+1
                    fake_product = {
                        'Id':decomposition['destination_Id'],
                        'level':level
                    }
                    self.get_product_decomposition(fake_product)
                    decomposition['next_level'] = fake_product['decompositions']
            else:
                a=1

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

        if attributes == None:  return

        for atttribute in attributes:
            print(f"{_path};{atttribute['att']}-{atttribute['pAtt']};{atttribute['type']};{atttribute['len']}")

    def print_decomposition(self,path,decompostions):
        spath = path.copy()
        while len(spath)<8:
            spath.append("")

        _path = ";".join(spath)

        if decompostions == None:      return

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

        if attributes == None: return
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