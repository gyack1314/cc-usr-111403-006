"""同一目录实例中的CAS表提交和完整变更日志。"""
from copy import deepcopy
from threading import RLock
from .storage import digest

class Table:
    def __init__(self,rows):
        self._lock=RLock();self._rows=self._index(rows);self.seq=0;self.log=[];self.history=[self.snapshot()]
    def _index(self,rows):
        out={}
        for row in deepcopy(rows):
            rid=row['row_id']
            if rid in out:raise ValueError('行身份重复')
            out[rid]=row
        return out
    def snapshot(self):
        with self._lock:
            rows=[deepcopy(self._rows[k]) for k in sorted(self._rows)]
            return {'seq':self.seq,'rows':rows,'rows_digest':digest(rows)}
    def commit(self,expected_seq,op,**args):
        with self._lock:
            if expected_seq!=self.seq:raise ValueError('表版本冲突')
            before=deepcopy(self._rows);after=deepcopy(before)
            if op=='append':
                for rid,row in self._index(args['rows']).items():
                    if rid in after:raise ValueError('行已存在')
                    after[rid]=row
            elif op=='update':
                rid=args['row_id']
                if 'row_id' in args['values'] and args['values']['row_id']!=rid:raise ValueError('不能改行身份')
                after[rid].update(deepcopy(args['values']))
            elif op=='delete':del after[args['row_id']]
            elif op=='replace_partition':
                field=args['field'];value=args['value'];replacement=self._index(args['rows'])
                if any(r[field]!=value for r in replacement.values()):raise ValueError('替换分区不一致')
                after={k:r for k,r in after.items() if r[field]!=value}
                if set(after)&set(replacement):raise ValueError('替换行身份冲突')
                after.update(replacement)
            else:raise ValueError('未知写入操作')
            changes=[{'row_id':k,'old':before.get(k),'new':after.get(k)} for k in sorted(set(before)|set(after)) if before.get(k)!=after.get(k)]
            self._rows=after;self.seq+=1
            self.log.append({'seq':self.seq,'op':op,'changes':changes});snap=self.snapshot();self.history.append(snap);return snap
    def changes(self,after,through):
        if not 0<=after<=through<=self.seq:raise ValueError('日志范围非法')
        return deepcopy(self.log[after:through])
