import operator


class DynamoChain:
    def __init__(self, table) -> None:
        self._table = table
        self._query = {}
        self._operator = operator.and_

    def _check_next_query(self, resp):
        if "LastEvaluetedKey" in resp:
            self._query["ExclusiveStartKey"] = resp["LastEvaluetedKey"]
        else:
            self._query.pop("ExclusiveStartKey", None)

    def clear(self):
        self._query = {}
        self._operator = operator.and_

    @property
    def and_(self):
        self._operator = operator.and_
        return self

    @property
    def or_(self):
        self._operator = operator.or_
        return self

    @property
    def done(self):
        return not "ExclusiveStartKey" in self._query

    # Chain Method
    def key_condition(self, kce):
        if "KeyConditionExpression" in self._query:
            self._query["KeyConditionExpression"] &= kce
        else:
            self._query["KeyConditionExpression"] = kce
        return self

    def filter(self, fe):
        if "FilterExpression" in self._query:
            self._query["FilterExpression"] = self._operator(
                self._query["FilterExpression"], fe
            )
        else:
            self._query["FilterExpression"] = fe
        return self

    def limit(self, num):
        self._query["Limit"] = num
        return self

    def asc(self):
        self._query["ScanIndexForward"] = True
        return self

    def desc(self):
        self._query["ScanIndexForward"] = False
        return self

    def key(self, key, value):
        if "Key" in self._query:
            self._query["Key"] |= {key: value}
        else:
            self._query["Key"] = {key: value}
        return self

    def consistent_read(self, cr=True):
        self._query["ConsistentRead"] = cr
        return self

    # Last Method
    def count(self):
        self._query["Select"] = "COUNT"
        resp = self._table.scan(**self._query)
        self._check_next_query(resp)
        count = resp["Count"]
        return count

    def count_all(self):
        resp = self.count()
        while not self.done:
            resp += self.count()
        return resp

    def scan(self):
        resp = self._table.scan(**self._query)
        self._check_next_query(resp)
        return resp["Items"]

    def scan_all(self):
        resp = self.scan()
        while not self.done:
            resp += self.scan()
        return resp

    def query(self):
        resp = self._table.query(**self._query)
        self._check_next_query(resp)
        return resp["Items"]

    def query_all(self):
        resp = self.query()
        while not self.done:
            resp += self.query()
        return resp

    def delete(self):
        self._table.delete_item(**self._query)

    def get(self):
        return self._table.get_item(**self._query)["Item"]
