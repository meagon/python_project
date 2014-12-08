

def json_unicode2utf8_convert(input):
    if isinstance(input, dict):
        return {json_unicode2utf8_convert(key): json_unicode2utf8_convert(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [json_unicode2utf8_convert(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

