from dataclasses import dataclass
from typing import Union, List
import base64

from dataclasses_json import dataclass_json

from practicuscore.api_base import ConnConf, NodeFileConnConf, SqLiteConnConf, S3ConnConf, MYSQLConnConf, \
    PostgreSQLConnConf, RedshiftConnConf, SnowflakeConnConf, MSSQLConnConf, OracleConnConf, HiveConnConf, \
    AthenaConnConf, ElasticSearchConnConf, OpenSearchConnConf, CustomDBConnConf, TrinoConnConf, HanaConnConf, \
    TeradataConnConf, Db2ConnConf, DynamoDBConnConf, CockroachDBConnConf, ClouderaConnConf


@dataclass_json
@dataclass
class DefinedConnectionConfiguration:
    uuid: str
    key: str
    cloud: str
    region_name: str
    conn_conf: Union[
        ConnConf,
        NodeFileConnConf,
        SqLiteConnConf,
        S3ConnConf,
        MYSQLConnConf,
        PostgreSQLConnConf,
        RedshiftConnConf,
        SnowflakeConnConf,
        MSSQLConnConf,
        OracleConnConf,
        HiveConnConf,
        AthenaConnConf,
        ElasticSearchConnConf,
        OpenSearchConnConf,
        TrinoConnConf,
        HanaConnConf,
        TeradataConnConf,
        Db2ConnConf,
        DynamoDBConnConf,
        CockroachDBConnConf,
        ClouderaConnConf,
        CustomDBConnConf,
    ]
    can_write: bool = True


@dataclass_json
@dataclass
class DefinedConnectionConfigurations:
    defined_conn_conf_list: List[DefinedConnectionConfiguration]

    def to_base64_str(self) -> str:
        return str(base64.b64encode(bytes(self.to_json(), encoding="utf-8")), "utf-8")

    @staticmethod
    def from_base64_str(data: str) -> 'DefinedConnectionConfigurations':
        json = str(base64.b64decode(data), "utf-8")
        return DefinedConnectionConfigurations.from_json(json)


# if __name__ == '__main__':
#     cn_cnf = NodeFileConnConf(file_path="/users/blah")
#     a = DefinedConnectionConfiguration(uuid="a", key="a", cloud="a", region_name="a", conn_conf=cn_cnf)
#     cn_cnf2 = NodeFileConnConf(file_path="/users/blah2")
#     b = DefinedConnectionConfiguration(uuid="b", key="b", cloud="b", region_name="b", conn_conf=cn_cnf2)
#
#     l = DefinedConnectionConfigurations(defined_conn_conf_list=[a, b])
#
#     _json = l.to_json()
#     print(_json)
#     l2 = DefinedConnectionConfigurations.from_json(_json)
#
#     print(l2.defined_conn_conf_list[1].uuid)
#
#     b64 = l2.to_base64_str()
#     print(b64)
#     l3 = DefinedConnectionConfigurations.from_base64_str(b64)
#     print(l3.to_json())
