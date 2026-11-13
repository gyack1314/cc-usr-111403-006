"""行级CHECK表达式的三值语义。"""
def validate(expr):
    op=expr['op']
    if op in ('and','or'):
        if len(expr['args'])<2:raise ValueError('布尔参数不足')
        for e in expr['args']:validate(e)
    elif op=='not':validate(expr['arg'])
    elif op in ('ge','gt','eq','le','lt','is_null'):
        if not isinstance(expr['field'],str):raise ValueError('列身份非法')
    else:raise ValueError('未知约束表达式')

def evaluate(expr,row):
    validate(expr);op=expr['op']
    if op in ('and','or'):
        values=[evaluate(e,row) for e in expr['args']]
        if op=='and':return False if False in values else (None if None in values else True)
        return True if True in values else (None if None in values else False)
    if op=='not':
        v=evaluate(expr['arg'],row);return None if v is None else not v
    a=row[expr['field']]
    if op=='is_null':return a is None
    b=expr['value']
    if a is None or b is None:return None
    return {'ge':lambda:a>=b,'gt':lambda:a>b,'eq':lambda:a==b,'le':lambda:a<=b,'lt':lambda:a<b}[op]()

def accepted(expr,row):return evaluate(expr,row) is not False
