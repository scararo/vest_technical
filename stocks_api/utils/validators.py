import json

class ValidatorView(object):

    def __init__(self, request, to_serialize):

        if request.method=='POST':
            body = request.body
            self.data = json.loads(body)
        
        if request.method=='GET':
            self.data = request.GET

        if to_serialize == 'trade_view':
            self.class_to_use = ValidatorTradeView(self.data) 

        if to_serialize == 'share_by_hour':
            self.class_to_use = ValidatorSharesByHour(self.data)

        if to_serialize == 'check_code':
            self.class_to_use = ValidatorCheckCode(self.data)

        if to_serialize == 'held_shares':
            self.class_to_use = ValidatorHeldShares(self.data)


        self.parser_data, self.is_valid = self.class_to_use.parser_data


class ValidatorBase(object):

    serializer_keys=None
    optional_keys = None

    def __init__(self, data):
        
        self.data = data


    @property
    def parser_data(self):
    
        errors=[]
        valid_output={}
        for key in self.serializer_keys:
            if key in self.data:
                valid_output[key] = self.data[key]
            else:
                errors.append({key: 'missing field'})
        if errors:
            return {"errors": errors}, False
        else:
            return valid_output, True



class ValidatorTradeView(ValidatorBase):

    serializer_keys= {'symbol', 'amount', 'action'}


class ValidatorSharesByHour(ValidatorBase):

    serializer_keys={'username', 'init-time'}


class ValidatorCheckCode(ValidatorBase):

    serializer_keys = {'code'}


class ValidatorHeldShares(ValidatorBase):

    serializer_keys = {'code'}


def validate_input_from_trade_view(**kwargs):

    keys_parameters = {'username', 'symbol', 'amount', 'action'}
    valid_output={}
    errors=[]

    for key in keys_parameters:
        if key in kwargs.keys():
            valid_output[key] = kwargs[key]
        else:
            errors.append({key: 'missing field'})

    if errors:
        return {"errors": errors}
    else:
        return valid_output


def validate_input_from_get_share_by_hour(**kwargs):

    key_parameters = {'init_time'}
     