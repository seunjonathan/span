'''
    This file is the set of flatten commands that are used by the unit test cases.
    For now, this file only contains those flatten commands that appear in more than one unit test.
    We capture them here so that we don't accidently generate multiple copies or versions of them in the main
    unit test code.

    CAUTION: I have come across "unexpected control character" errors thrown by json.loads() in Databricks
             when the flatten command has newlines in it.
'''

FLATTEN_COMMAND_MISSES_SHORE_POWER_UTILIZATION = '''
            select
            min(ended_at) as ended_at
            , id
            , min(leg_from_id)                          as leg_from_id
            , min(leg_from_name)                        as leg_from_name
            , min(leg_from_type)                        as leg_from_type
            , min(leg_to_id)                            as leg_to_id
            , min(leg_to_name)                          as leg_to_name
            , min(leg_to_type)                          as leg_to_type
            , min(disconnected_at)                      as disconnected_at
            , min(undocked_at)                          as undocked_at
            , array_join(collect_set(reasons_type),',') as reasons_type
            , min(connected_at)                         as connected_at
            , min(docked_at)                            as docked_at
            , min(started_at)                           as started_at
            , min(additional_emissions)                 as additional_emissions
            , min(duration_min)                         as duration_min
            , min(target_id)                            as target_id
            , min(target_type)                          as target_type
            , min(tenant_id)                            as tenant_id
            , min(vessel_id)                            as vessel_id
            , min(voyage_number)                        as voyage_number
            from
            (
                select
                ended_at
                , id
                , get_json_object(to_json(entries), '$.leg.from.id') as leg_from_id
                , get_json_object(to_json(entries), '$.leg.from.name') as leg_from_name
                , get_json_object(to_json(entries), '$.leg.from.type') as leg_from_type
                , get_json_object(to_json(entries), '$.leg.to.id') as leg_to_id
                , get_json_object(to_json(entries), '$.leg.to.name') as leg_to_name
                , get_json_object(to_json(entries), '$.leg.to.type') as leg_to_type
                , reasons_info.disconnected_at
                , reasons_info.type as reasons_type
                , reasons_info.undocked_at
                , get_json_object(to_json(reasons_info), '$.connected_at') as connected_at
                , get_json_object(to_json(reasons_info), '$.docked_at') as docked_at
                , started_at
                , additional_emissions
                , duration_min
                , target.id   as target_id
                , target.type as target_type
                , tenant_id
                , vessel_id
                , get_json_object(to_json(entries), '$.voyage.number') as voyage_number
                from
                (
                    select *
                    , explode(reasons) as reasons_info
                    from
                    (
                        select *
                        , properties.*
                        from
                        (
                            select *
                            , statistics.*
                            from
                            (
                                select
                                entries,
                                entries.*
                                from
                                (
                                    select
                                    explode(entries) as entries
                                    from
                                    json
                                )
                            )
                        )
                    )
                )
            )
            group by id
        '''

FLATTEN_COMMAND_MISSES_DUAL_FUEL_ENGINE_GAS_MODE = '''
        select
            ended_at
            , id
            , get_json_object(to_json(entries), '$.leg.from.id') as leg_from_id
            , get_json_object(to_json(entries), '$.leg.from.name') as leg_from_name
            , get_json_object(to_json(entries), '$.leg.from.type') as leg_from_type
            , get_json_object(to_json(entries), '$.leg.to.id') as leg_to_id
            , get_json_object(to_json(entries), '$.leg.to.name') as leg_to_name
            , get_json_object(to_json(entries), '$.leg.to.type') as leg_to_type
            , properties.engine as properties_engine
            , started_at
            , statistics.duration_min
            , consumer_name
            , amount as fuel_amount
            , fuel_name
            , unit as fuel_unit
            , source
            , fuel_oil_emissions
            , target.id   as target_id
            , target.type as target_type
            , tenant_id
            , vessel_id
            , get_json_object(to_json(entries), '$.voyage.number') as voyage_number
        from
            (
            select *
                , get_json_object(to_json(statistics), '$.fuel_oil_consumption.consumer_name') as consumer_name
                , get_json_object(to_json(statistics), '$.fuel_oil_consumption.fuel_amount.amount') as amount
                , get_json_object(to_json(statistics), '$.fuel_oil_consumption.fuel_amount.unit') as unit
                , get_json_object(to_json(statistics), '$.fuel_oil_consumption.fuel_amount.name') as fuel_name
                , get_json_object(to_json(statistics), '$.fuel_oil_consumption.source') as source
                , get_json_object(to_json(statistics), '$.fuel_oil_emissions') as fuel_oil_emissions
            from
                (
                select *
                  ,  statistics
                from
                    (
                    select
                        entries,
                        entries.*
                    from
                        (
                        select
                            explode(entries) as entries
                        from
                            json
                        )
                    )
                )
            )
        '''

FLATTEN_COMMAND_MISSES_ENERGY_CONSUMPTION = '''
select
  ended_at
, id
, leg_from_id
, leg_from_name
, leg_from_type
, leg_to_id
, leg_to_name
, leg_to_type
, reason_actual_value
, reason_expected_value
, reason_predicate
, reason_type
, started_at
, duration_min
, target_id
, target_type
, tenant_id
, vessel_id
, voyage_number
from
  (
    select *
    , reason.type                  as reason_type
    , reason.reason.actual_value   as reason_actual_value
    , reason.reason.expected_value as reason_expected_value
    , reason.reason.predicate      as reason_predicate
    from
      (
        select *
        , explode(reasons) as reason
        from
          (
            select
              comments
            , ended_at
            , id
            , get_json_object(to_json(entries), '$.leg.from.id') as leg_from_id
            , get_json_object(to_json(entries), '$.leg.from.name') as leg_from_name
            , get_json_object(to_json(entries), '$.leg.from.type') as leg_from_type
            , get_json_object(to_json(entries), '$.leg.to.id') as leg_to_id
            , get_json_object(to_json(entries), '$.leg.to.name') as leg_to_name
            , get_json_object(to_json(entries), '$.leg.to.type') as leg_to_type
            , started_at
            , statistics.duration_min
            , properties.*
            , target.id   as target_id
            , target.type as target_type
            , tenant_id
            , vessel_id
            , get_json_object(to_json(entries), '$.voyage.number') as voyage_number
            from
              (
                select *
                from
                  (
                    select
                      entries
                    , entries.*
                    from
                      (
                        select
                          explode(entries) as entries
                        from
                          json
                      )
                  )
              )
          )
      )
  )
'''
