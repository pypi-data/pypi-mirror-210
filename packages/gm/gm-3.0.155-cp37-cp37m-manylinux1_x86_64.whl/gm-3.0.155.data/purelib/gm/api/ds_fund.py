from typing import List, Dict, Any

import numpy as np
import pandas as pd

from gm.api._errors import check_gm_status
from gm.pb_to_dict import protobuf_to_dict
from gm.csdk.c_sdk import (
    py_gmi_stk_get_industry_category,
    py_gmi_stk_get_industry_constituents,
    py_gmi_stk_get_symbol_industry,
    py_gmi_stk_get_index_constituents,
    py_gmi_stk_get_index_history_constituents,
    py_gmi_stk_get_dividend,
    py_gmi_stk_get_adj_factor,
    py_gmi_fut_get_continuous_contracts,
    py_gmi_fut_get_contract_info,
    py_gmi_fnd_get_adj_factor,
    py_gmi_fnd_get_dividend,
    py_gmi_fnd_get_split,

    py_gmi_stk_get_sector_category,
    py_gmi_stk_get_sector_constituents,
    py_gmi_stk_get_symbol_sector,
    py_stk_get_ration,
    py_gmi_stk_get_shareholder_num,
    py_gmi_stk_get_top_shareholder,
    py_gmi_stk_get_share_change,
    py_gmi_stk_get_fundamentals_balance,
    py_gmi_stk_get_fundamentals_cashflow,
    py_gmi_stk_get_fundamentals_income,
    py_gmi_stk_get_fundamentals_balance_pt,
    py_gmi_stk_get_fundamentals_cashflow_pt,
    py_gmi_stk_get_fundamentals_income_pt,
    py_gmi_fut_get_transaction_ranking,
    py_gmi_fut_get_warehouse_receipt,
    py_gmi_fnd_get_etf_constituents,
    py_gmi_fnd_get_portfolio,
    py_gmi_fnd_get_net_value,
    py_gmi_bnd_get_conversion_price,
    py_gmi_bnd_get_call_info,
    py_gmi_bnd_get_put_info,
    py_gmi_bnd_get_amount_change,
)
from gm.pb.fund_stk_service_pb2 import (
    GetIndustryCategoryReq, GetIndustryCategoryRsp,
    GetIndustryConstituentsReq, GetIndustryConstituentsRsp,
    GetSymbolIndustryReq, GetSymbolIndustryRsp,
    GetIndexConstituentsReq, GetIndexConstituentsRsp,
    GetIndexHistoryConstituentsReq, GetIndexHistoryConstituentsRsp,
    GetDividendReq, GetDividendRsp,
    GetAdjFactorReq, GetAdjFactorRsp,
    GetSectorCategoryReq, GetSectorCategoryRsp,
    GetSectorConstituentsReq, GetSectorConstituentsRsp,
    GetSymbolSectorReq, GetSymbolSectorRsp,
    GetRationReq, GetRationRsp,
    GetShareholderNumReq, GetShareholderNumRsp,
    GetTopShareholderReq, GetTopShareholderRsp,
    GetShareChangeReq, GetShareChangeRsp,
    GetFundamentalsBalanceReq, GetFundamentalsBalanceRsp,
    GetFundamentalsCashflowReq, GetFundamentalsCashflowRsp,
    GetFundamentalsIncomeReq, GetFundamentalsIncomeRsp,
    GetFundamentalsBalancePtReq, GetFundamentalsBalancePtRsp,
    GetFundamentalsCashflowPtReq, GetFundamentalsCashflowPtRsp,
    GetFundamentalsIncomePtReq, GetFundamentalsIncomePtRsp,
)
from gm.pb.fund_fut_service_pb2 import (
    GetContinuousContractsReq, GetContinuousContractsRsp,
    FutGetContractInfoReq, FutGetContractInfoRsp,
    FutGetTransactionRankingReq, FutGetTransactionRankingRsp,
    GetWarehouseReceiptReq, GetWarehouseReceiptRsp,
)
from gm.pb.fund_fnd_service_pb2 import (
    FndGetAdjFactorReq, FndGetAdjFactorRsp,
    FndGetDividendReq, FndGetDividendRsp,
    GetSplitReq, GetSplitRsp,
    GetEtfConstituentsReq, GetEtfConstituentsRsp,
    GetPortfolioReq, GetPortfolioRsp,
    GetNetValueReq, GetNetValueRsp,
)
from gm.pb.fund_bnd_service_pb2 import (
    GetConversionPriceReq, GetConversionPriceRsp,
    GetCallInfoReq, GetCallInfoRsp,
    GetPutInfoReq, GetPutInfoRsp,
    GetAmountChangeReq, GetAmountChangeRsp,
)


_int_fields = ["data_type", "rpt_type"]
_str_fields = ["begin_dt", "curr"]


def _extract_data(result):
    data = []
    for item in result.get("data", []):
        for k, v in item["data"].items():
            if k in _int_fields:
                item[k] = int(v)
            elif k in _str_fields:
                item[k] = v
            # dicimal 类型
            elif v == "":
                item[k] = np.NAN
            else:
                item[k] = float(v)
        del item["data"]
        data.append(item)
    return data


def stk_get_industry_category(source="zjh2012", level=1):
    # type: (str, int) -> pd.DataFrame
    """
    查询行业分类

    * source: 行业来源, 默认值 'zjh2012'
    * level: 行业分级, 默认值 1, (1:一级行业, 2:二级行业, 3:三级行业)
    """
    req = GetIndustryCategoryReq(
        source=source,
        level=level,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_industry_category(req)
    check_gm_status(status)
    res = GetIndustryCategoryRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, str]]
    return pd.DataFrame(data)


def stk_get_industry_constituents(industry_code, date=""):
    # type: (str, str) -> pd.DataFrame
    """
    查询行业成分股
    """
    req = GetIndustryConstituentsReq(
        industry_code=industry_code,
        date=date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_industry_constituents(req)
    check_gm_status(status)
    res = GetIndustryConstituentsRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict]
    return pd.DataFrame(data)


def stk_get_symbol_industry(symbols, source="zjh2012", level=1, date=""):
    # type: (str|List[str], str, int, str) -> pd.DataFrame
    """
    查询股票的所属行业

    证监会行业分类2012没有三级行业, 若输入source='zjh2012', level=3则参数无效, 返回空
    """
    if isinstance(symbols, str):
        symbols = [symbol.strip() for symbol in symbols.split(",")]
    req = GetSymbolIndustryReq(
        symbols=symbols,
        source=source,
        level=level,
        date=date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_symbol_industry(req)
    check_gm_status(status)
    res = GetSymbolIndustryRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, str]]
    return pd.DataFrame(data)


def stk_get_sector_category(sector_type):
    # type: (str) -> pd.DataFrame
    """
    查询板块分类
    """
    req = GetSectorCategoryReq(
        sector_type=sector_type,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_sector_category(req)
    check_gm_status(status)
    rsp = GetSectorCategoryRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])  # type: List[Dict[str, str]]
    return pd.DataFrame(data)


def stk_get_sector_constituents(sector_code):
    # type: (str) -> pd.DataFrame
    """
    查询板块成分股
    """
    req = GetSectorConstituentsReq(
        sector_code=sector_code,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_sector_constituents(req)
    check_gm_status(status)
    rsp = GetSectorConstituentsRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])  # type: List[Dict[str, str]]
    return pd.DataFrame(data)


def stk_get_symbol_sector(symbols, sector_type):
    # type: (str|List[str], str) -> pd.DataFrame
    """
    查询股票的所属板块
    """
    if isinstance(symbols, str):
        symbols = [symbol.strip() for symbol in symbols.split(",")]
    req = GetSymbolSectorReq(
        symbols=symbols,
        sector_type=sector_type,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_symbol_sector(req)
    check_gm_status(status)
    rsp = GetSymbolSectorRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])  # type: List[Dict[str, str]]
    return pd.DataFrame(data)


def stk_get_index_constituents(index, trade_date=None):
    # type: (str, str) -> pd.DataFrame
    """
    查询指数最新成分股
    """
    req = GetIndexConstituentsReq(
        index=index,
        trade_date=trade_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_index_constituents(req)
    check_gm_status(status)
    res = GetIndexConstituentsRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def stk_get_index_history_constituents(index, start_date="", end_date=""):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询指数历史成分股
    """
    req = GetIndexHistoryConstituentsReq(
        index=index,
        start_date=start_date,
        end_date=end_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_index_history_constituents(req)
    check_gm_status(status)
    res = GetIndexHistoryConstituentsRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])  # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def stk_get_dividend(symbol, start_date, end_date):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询股票分红送股信息
    """
    req = GetDividendReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )

    req = req.SerializeToString()
    status, result = py_gmi_stk_get_dividend(req)
    check_gm_status(status)
    res = GetDividendRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def stk_get_ration(symbol, start_date, end_date):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询股票配股信息
    """
    req = GetRationReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )

    req = req.SerializeToString()
    status, result = py_stk_get_ration(req)
    check_gm_status(status)
    res = GetRationRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def stk_get_adj_factor(symbol, start_date="", end_date="", base_date=""):
    # type: (str, str, str, str) -> pd.DataFrame
    """
    查询股票的复权因子
    """
    req = GetAdjFactorReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        base_date=base_date,
    )

    req = req.SerializeToString()
    status, result = py_gmi_stk_get_adj_factor(req)
    check_gm_status(status)
    res = GetAdjFactorRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, str|float]]
    return pd.DataFrame(data)


def stk_get_shareholder_num(symbol, start_date="", end_date=""):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询股东户数
    """
    req = GetShareholderNumReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )

    req = req.SerializeToString()
    status, result = py_gmi_stk_get_shareholder_num(req)
    check_gm_status(status)
    res = GetShareholderNumRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def stk_get_top_shareholder(symbol, start_date="", end_date="", tradable_holder=False):
    # type: (str, str, str, bool) -> pd.DataFrame
    """
    查询十大股东
    """
    req = GetTopShareholderReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        tradable_holder=tradable_holder,
    )

    req = req.SerializeToString()
    status, result = py_gmi_stk_get_top_shareholder(req)
    check_gm_status(status)
    res = GetTopShareholderRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def stk_get_share_change(symbol, start_date="", end_date=""):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询股本变动
    """
    req = GetShareChangeReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )

    req = req.SerializeToString()
    status, result = py_gmi_stk_get_share_change(req)
    check_gm_status(status)
    res = GetShareChangeRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def stk_get_fundamentals_balance(symbol, fields, rpt_type=None, data_type=None, start_date=None, end_date=None, df=False):
    # type: (str, str, int, int, str, str, bool) -> pd.DataFrame | List[Dict]
    """查询资产负债表数据"""
    if rpt_type is None:
        rpt_type = 0
    if data_type is None:
        data_type = 0
    if start_date is None:
        start_date = ""
    if end_date is None:
        end_date = ""
    if fields is None:
        fields = ""
    else:
        fields = [field.strip() for field in fields.split(",")]

    req = GetFundamentalsBalanceReq(
        symbol=symbol,
        rpt_type=rpt_type,
        data_type=data_type,
        start_date=start_date,
        end_date=end_date,
        fields=fields,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_fundamentals_balance(req)
    check_gm_status(status)

    data = []
    rsp = GetFundamentalsBalanceRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = _extract_data(result)
    if df:
        return pd.DataFrame(data)
    return data


def stk_get_fundamentals_balance_pt(symbols, fields, rpt_type=None, data_type=None, date=None, df=False):
    # type: (str, str, int, int, str, bool) -> pd.DataFrame | List[Dict]
    """查询资产负债表截面数据"""
    if isinstance(symbols, str):
        symbols = [symbol.strip() for symbol in symbols.split(",")]
    if rpt_type is None:
        rpt_type = 0
    if data_type is None:
        data_type = 0
    if date is None:
        date = ""
    if fields is None:
        fields = ""
    else:
        fields = [field.strip() for field in fields.split(",")]

    req = GetFundamentalsBalancePtReq(
        symbols=symbols,
        rpt_type=rpt_type,
        data_type=data_type,
        date=date,
        fields=fields,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_fundamentals_balance_pt(req)
    check_gm_status(status)
    data = []
    rsp = GetFundamentalsBalancePtRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = _extract_data(result)
    if df:
        return pd.DataFrame(data)
    return data


def stk_get_fundamentals_cashflow(symbol, fields, rpt_type=None, data_type=None, start_date=None, end_date=None, df=False):
    # type: (str, str, int, int, str, str, bool) -> pd.DataFrame | List[Dict]
    """查询现金流量表数据"""
    if rpt_type is None:
        rpt_type = 0
    if data_type is None:
        data_type = 0
    if start_date is None:
        start_date = ""
    if end_date is None:
        end_date = ""
    if fields is None:
        fields = ""
    else:
        fields = [field.strip() for field in fields.split(",")]

    req = GetFundamentalsCashflowReq(
        symbol=symbol,
        rpt_type=rpt_type,
        data_type=data_type,
        start_date=start_date,
        end_date=end_date,
        fields=fields,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_fundamentals_cashflow(req)
    check_gm_status(status)
    data = []
    rsp = GetFundamentalsCashflowRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = _extract_data(result)
    if df:
        return pd.DataFrame(data)
    return data


def stk_get_fundamentals_cashflow_pt(symbols, fields, rpt_type=None, data_type=None, date=None, df=False):
    # type: (str, str, int, int, str, bool) -> pd.DataFrame | List[Dict]
    """查询现金流量表截面数据"""
    if isinstance(symbols, str):
        symbols = [symbol.strip() for symbol in symbols.split(",")]
    if rpt_type is None:
        rpt_type = 0
    if data_type is None:
        data_type = 0
    if date is None:
        date = ""
    if fields is None:
        fields = ""
    else:
        fields = [field.strip() for field in fields.split(",")]

    req = GetFundamentalsCashflowPtReq(
        symbols=symbols,
        rpt_type=rpt_type,
        data_type=data_type,
        date=date,
        fields=fields,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_fundamentals_cashflow_pt(req)
    check_gm_status(status)
    data = []
    rsp = GetFundamentalsCashflowPtRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = _extract_data(result)
    if df:
        return pd.DataFrame(data)
    return data


def stk_get_fundamentals_income(symbol, fields, rpt_type=None, data_type=None, start_date=None, end_date=None, df=False):
    # type: (str, str, int, int, str, str, bool) -> pd.DataFrame | List[Dict]
    """查询利润表数据"""
    if rpt_type is None:
        rpt_type = 0
    if data_type is None:
        data_type = 0
    if start_date is None:
        start_date = ""
    if end_date is None:
        end_date = ""
    if fields is None:
        fields = []
    else:
        fields = [field.strip() for field in fields.split(",")]

    req = GetFundamentalsIncomeReq(
        symbol=symbol,
        rpt_type=rpt_type,
        data_type=data_type,
        start_date=start_date,
        end_date=end_date,
        fields=fields,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_fundamentals_income(req)
    check_gm_status(status)
    data = []
    rsp = GetFundamentalsIncomeRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = _extract_data(result)
    if df:
        data = pd.DataFrame(data)
    return data


def stk_get_fundamentals_income_pt(symbols, fields, rpt_type=None, data_type=None, date=None, df=False):
    # type: (str, str, int, int, str, bool) -> pd.DataFrame | List[Dict]
    """查询利润表截面数据"""
    if isinstance(symbols, str):
        symbols = [symbol.strip() for symbol in symbols.split(",")]
    if rpt_type is None:
        rpt_type = 0
    if data_type is None:
        data_type = 0
    if date is None:
        date = ""
    if fields is None:
        fields = []
    else:
        fields = [field.strip() for field in fields.split(",")]

    req = GetFundamentalsIncomePtReq(
        symbols=symbols,
        rpt_type=rpt_type,
        data_type=data_type,
        date=date,
        fields=fields,
    )
    req = req.SerializeToString()
    status, result = py_gmi_stk_get_fundamentals_income_pt(req)
    check_gm_status(status)
    data = []
    rsp = GetFundamentalsIncomePtRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = _extract_data(result)
    if df:
        data = pd.DataFrame(data)
    return data


def fut_get_continuous_contracts(csymbol, start_date="", end_date=""):
    # type: (str, str, str) -> List[Dict[str, Any]]
    """
    查询连续合约对应的真实合约
    """
    req = GetContinuousContractsReq(
        csymbol=csymbol,
        start_date=start_date,
        end_date=end_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_fut_get_continuous_contracts(req)
    check_gm_status(status)
    res = GetContinuousContractsRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, str]]
    return data


def fut_get_contract_info(product_codes, df=False):
    # type: (str|List[str], bool) -> List[Dict[str, str|int]] | pd.DataFrame
    """
    查询期货标准品种信息
    """
    if isinstance(product_codes, str):
        product_codes = [code.strip() for code in product_codes.split(",")]
    req = FutGetContractInfoReq(
        product_codes=product_codes,
    )

    req = req.SerializeToString()
    status, result = py_gmi_fut_get_contract_info(req)
    check_gm_status(status)
    res = FutGetContractInfoRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, str|int]]
    if df:
        return pd.DataFrame(data)
    return data


def fut_get_transaction_ranking(symbol, trade_date="", indicator="volume"):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询期货每日成交持仓排名
    """
    req = FutGetTransactionRankingReq(
        symbol=symbol,
        trade_date=trade_date,
        indicator=indicator,
    )

    req = req.SerializeToString()
    status, result = py_gmi_fut_get_transaction_ranking(req)
    check_gm_status(status)
    rsp = FutGetTransactionRankingRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    data = pd.DataFrame(data)   # type: pd.DataFrame
    if data.empty:
        return data
    # ranking_change_is_null 字段用于判断 ranking_change 是否为空, 最终输出需要删除这个字段
    data.loc[data["ranking_change_is_null"] == True, "ranking_change"] = None
    return data.drop(axis=1, columns="ranking_change_is_null")


def fut_get_warehouse_receipt(product_code, start_date="", end_date=""):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询期货仓单数据
    """
    req = GetWarehouseReceiptReq(
        product_code=product_code,
        start_date=start_date,
        end_date=end_date,
    )

    req = req.SerializeToString()
    status, result = py_gmi_fut_get_warehouse_receipt(req)
    check_gm_status(status)
    rsp = GetWarehouseReceiptRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def fnd_get_etf_constituents(etf):
    # type: (str) -> pd.DataFrame
    """
    查询ETF最新成分股
    """
    req = GetEtfConstituentsReq(
        etf=etf,
    )
    req = req.SerializeToString()
    status, result = py_gmi_fnd_get_etf_constituents(req)
    check_gm_status(status)
    rsp = GetEtfConstituentsRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def fnd_get_portfolio(fund, report_type, portfolio_type, start_date="", end_date=""):
    # type: (str, int, str, str, str) -> pd.DataFrame
    """
    查询基金的资产组合
    """
    req = GetPortfolioReq(
        fund=fund,
        start_date=start_date,
        end_date=end_date,
        report_type=report_type,
        portfolio_type=portfolio_type,
    )
    req = req.SerializeToString()
    status, result = py_gmi_fnd_get_portfolio(req)
    check_gm_status(status)
    rsp = GetPortfolioRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    if portfolio_type == "stk":
        data = result.get("portfolio_stock", [])
    elif portfolio_type == "bnd":
        data = result.get("portfolio_bond", [])
    elif portfolio_type == "fnd":
        data = result.get("portfolio_fund", [])
    else:
        data = []
    return pd.DataFrame(data)


def fnd_get_net_value(fund, start_date="", end_date=""):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询基金的净值数据
    """
    req = GetNetValueReq(
        fund=fund,
        start_date=start_date,
        end_date=end_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_fnd_get_net_value(req)
    check_gm_status(status)
    rsp = GetNetValueRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def fnd_get_adj_factor(fund, start_date="", end_date="", base_date=""):
    # type: (str, str, str, str) -> pd.DataFrame
    """
    查询基金复权因子
    """
    req = FndGetAdjFactorReq(
        fund=fund,
        start_date=start_date,
        end_date=end_date,
        base_date=base_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_fnd_get_adj_factor(req)
    check_gm_status(status)
    res = FndGetAdjFactorRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, str|float]]
    return pd.DataFrame(data)


def fnd_get_dividend(fund, start_date, end_date):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询基金分红信息
    """
    req = FndGetDividendReq(
        fund=fund,
        start_date=start_date,
        end_date=end_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_fnd_get_dividend(req)
    check_gm_status(status)
    res = FndGetDividendRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def fnd_get_split(fund, start_date, end_date):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询基金分红信息
    """
    req = GetSplitReq(
        fund=fund,
        start_date=start_date,
        end_date=end_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_fnd_get_split(req)
    check_gm_status(status)
    res = GetSplitRsp()
    res.ParseFromString(result)
    result = protobuf_to_dict(res, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def bnd_get_conversion_price(symbol, start_date="", end_date=""):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询可转债转股价变动信息
    """
    req = GetConversionPriceReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_bnd_get_conversion_price(req)
    check_gm_status(status)
    rsp = GetConversionPriceRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def bnd_get_call_info(symbol, start_date="", end_date=""):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询可转债赎回信息
    """
    req = GetCallInfoReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_bnd_get_call_info(req)
    check_gm_status(status)
    rsp = GetCallInfoRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def bnd_get_put_info(symbol, start_date="", end_date=""):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询可转债回售信息
    """
    req = GetPutInfoReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_bnd_get_put_info(req)
    check_gm_status(status)
    rsp = GetPutInfoRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)


def bnd_get_amount_change(symbol, start_date="", end_date=""):
    # type: (str, str, str) -> pd.DataFrame
    """
    查询可转债剩余规模变动信息
    """
    req = GetAmountChangeReq(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
    )
    req = req.SerializeToString()
    status, result = py_gmi_bnd_get_amount_change(req)
    check_gm_status(status)
    rsp = GetAmountChangeRsp()
    rsp.ParseFromString(result)
    result = protobuf_to_dict(rsp, datetime_to_str=True)
    data = result.get("data", [])   # type: List[Dict[str, Any]]
    return pd.DataFrame(data)
