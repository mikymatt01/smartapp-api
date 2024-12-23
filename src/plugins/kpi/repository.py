

from typing import List
from sympy import sympify, zoo
from .schema import KPI, Configuration, ComputedValue, KPIOverview, KPIDetail
from src.utils import get_collection
from src.custom_exceptions import KPINotFoundException

from pymongo.collection import Collection

from fastapi import Request
from bson import ObjectId
import math

async def computeKPIByMachine(
    machine_id, 
    kpi_id, 
    start_date, 
    end_date, 
    granularity_days, 
    granularity_op,
    request: Request | None = None,
    kpis_collection: Collection[KPI] | None = None
) -> List[ComputedValue]:
    '''
    machine_id: id of the machine
    kpi: kpi name
    start_date
    end_date
    granularity_days: number of days to subaggregate data
    granularity_operation: sum, avg, min, max
    '''
    kpis_collection = get_collection(request, kpis_collection, "kpis")

    kpi_obj = await getKPIById(kpi_id, request=request, kpis_collection=kpis_collection)
    

    if kpi_obj.config.formula != None:
        res = await computeCompositeKPIByMachine(
            machine_id, 
            kpi_id, 
            start_date, 
            end_date, 
            granularity_days, 
            granularity_op,
            request,
            kpis_collection
        )
    else:
        res = await computeAtomicKPIByMachine(
            machine_id, 
            kpi_id, 
            start_date, 
            end_date, 
            granularity_days, 
            granularity_op,
            request,
            kpis_collection=kpis_collection
        )
    return res

async def computeCompositeKPIByMachine(
    machine_id, 
    kpi_id, 
    start_date, 
    end_date, 
    granularity_days, 
    granularity_op,
    request: Request,
    kpis_collection: Collection[KPI]
) -> List[ComputedValue]:
    kpi_obj = await getKPIById(kpi_id, request, kpis_collection=kpis_collection)
    

    if kpi_obj is None:
        raise Exception('KPI not found')
    
    
    children = kpi_obj.config.children
    formula = kpi_obj.config.formula
    values = []
    for child in children:
        kpi_dep = await getKPIById(child, request, kpis_collection=kpis_collection)
        value = await computeKPIByMachine(
            machine_id,
            kpi_dep.id, 
            start_date,
            end_date,
            granularity_days, 
            granularity_op,
            request,
            kpis_collection=kpis_collection
        )
        values.append({ kpi_dep.name: value })

    value = values[0]
    key = next(iter(value.keys()))
    results = []
    for index in range(len(value[key])):
        symbol_dict = {}
        for v in values:
            k = next(iter(v.keys()))
            symbol_dict[k] = v[k][index].value
        parsed_expression = sympify(formula)
        result = parsed_expression.subs(symbol_dict)
        if result == zoo or result == None or math.isnan(result):
            result = 0 #raise Exception('invalid math operation')
        results.append(ComputedValue(value=result))
    return results

mappingOp = {
    'avg': {
        'op': 'avg',
        'data': 'avg'
    },
    'sum': {
        'op': 'sum',
        'data': 'sum'
    },
    'min': {
        'op': 'min',
        'data': 'min'
    },
    'max': {
        'op': 'max',
        'data': 'max'
    },
    'std': {
        'op': 'stdDevPop',
        'data': 'avg'
    },
}

async def computeAtomicKPIByMachine(
    machine_id, 
    kpi_id, 
    start_date, 
    end_date, 
    granularity_days, 
    granularity_op,
    request: Request,
    kpis_collection: Collection[KPI]

) -> List[ComputedValue]:
    kpis_collection = get_collection(request, kpis_collection, "kpis")
    pipeline = [
        {
            "$match": {
                "_id": ObjectId(kpi_id)
            }
        },
        {
            "$unwind": {
                "path": "$data"
            }
        },
        {
            "$match": {
                "data.machine_id": ObjectId(machine_id),
                "data.datetime": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
        },
        {
            "$group": {
                "_id": None,
                "documents": {
                    "$push": "$$ROOT"
                }
            }
        },
        {
            "$unwind": {
                "path": "$documents",
                "includeArrayIndex": "index"
            }
        },
        {
            "$addFields": {
                "groupIndex": {
                    "$floor": {
                        "$divide": ["$index", granularity_days]
                    }
                }
            }
        },
        {
            "$group": {
                "_id": "$groupIndex",
                "value": {
                    f"${mappingOp[granularity_op]['op']}": f"$documents.data.{mappingOp[granularity_op]['data']}"
                }
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        },
        {
            "$project": {
                "_id": 0,
                "value": 1
            }
        }
    ]
    return [ComputedValue(**kpi) for kpi in await kpis_collection.aggregate(pipeline).to_list(None)]

async def getKPIByName(name: str, request: Request | None = None, kpis_collection: Collection[KPI] | None = None) -> KPIDetail:
    kpis_collection = get_collection(request, kpis_collection, "kpis")
    kpi = await kpis_collection.find_one({"name": name})
    return KPIDetail(**kpi) if kpi else None

async def getKPIById(id: str, request: Request | None = None, kpis_collection: Collection[KPI] | None = None) -> KPIDetail | KPIOverview:

    kpis_collection = get_collection(request, kpis_collection, "kpis")

    kpi = await kpis_collection.find_one({"_id": ObjectId(id)})

    if kpi is None:
        raise KPINotFoundException("KPI not found")
    

    kpi_detail = KPIDetail(**kpi)
    return kpi_detail
    

async def listKPIs(site: int, request: Request | None = None, kpis_collection: Collection[KPI] | None = None) -> List[KPIOverview]:
    sites_collection = get_collection(request, None, "sites")

    kpis = sites_collection.aggregate([
        {
            "$match":
            {
                "site_id": site
            }
        },
        {
            "$lookup":
            {
                "from": "kpis",
                "localField": "kpis_ids",
                "foreignField": "_id",
                "as": "kpis"
            }
        },
        {
            "$unwind":
            {
                "path": "$kpis"
            }
        },
        {
            "$project":
            {
                "_id": "$kpis._id",
                "name": "$kpis.name",
                "type": "$kpis.type",
                "description": "$kpis.description",
                "unite_of_measure": "$kpis.unite_of_measure"
            }
        }
    ])
    kpis = [KPIOverview(**kpi) async for kpi in kpis]

    if len(kpis) == 0:
        raise KPINotFoundException("No KPIs found")
    return kpis

async def listKPIsByName(names: List[str], request: Request | None = None, kpis_collection: Collection[KPI] | None = None) -> List[KPIOverview]:
    
    kpis_collection = get_collection(request, kpis_collection, "kpis")


    kpis = kpis_collection.find(
        { "name": { "$in": names } }, 
        {
        "_id": 1,
        "name": 1,
        "type": 1,
        "description": 1,
        "unite_of_measure": 1,
        }
    )

    kpis = [KPIOverview(**kpi) async for kpi in kpis]
    if len(kpis) == 0:
        raise KPINotFoundException("No KPIs found")
    
    return kpis

async def createKPI(
    name: str,
    type: str,
    description: str,
    unite_of_measure: str,
    children: List[str], 
    formula: str,
    request: Request | None = None,
    kpis_collection: Collection[KPI] | None = None
) -> KPIDetail:
    kpis_collection = get_collection(request, kpis_collection, "kpis")
    data = [] # what data should be stored here?
    kpi = KPI(
        name=name,
        type=type,
        description=description,
        unite_of_measure=unite_of_measure,
        data=data,
        config=Configuration(
            children=children, 
            formula=formula
        )
    )
    kpi_obj = kpi.model_dump(by_alias=True)
    kpi_obj["config"]["children"] = [ObjectId(kpi_id) for kpi_id in kpi_obj["config"]["children"]]
    result = await kpis_collection.insert_one(kpi_obj)
    created_kpi = await kpis_collection.find_one({"_id": result.inserted_id})
    return KPIDetail(**created_kpi)

async def deleteKPIByID(id: str, request: Request | None = None, kpis_collection: Collection[KPI] | None = None) -> bool:
    kpis_collection = get_collection(request, kpis_collection, "kpis")

    result = await kpis_collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0
