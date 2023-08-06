import typing
import nanoid
import datetime


def mongo_cache_request_and_pack(request_action: typing.Callable,
                                 is_success: typing.Callable,
                                 mongo_collection,
                                 query: typing.Dict,
                                 save_key: typing.Dict,
                                 fail_action: typing.Callable = None,
                                 mongo_cache_request_id_name='request_id',
                                 mongo_cache_response_name='response',
                                 mongo_cache_timestamp_name='claw_date',
                                 try_times=3) -> typing.Tuple[typing.Dict, str]:
    if try_times < 1:
        raise f"mongo_cache_request_and_pack 多次尝试失败"

    find = mongo_collection.find_one(query)
    if find:
        response = find.get(mongo_cache_response_name)
        request_id = find.get(mongo_cache_request_id_name)
        return response, request_id
    else:
        try:
            r = request_action()

            if r and is_success(r):
                request_id = nanoid.generate()

                save_key.update({
                    mongo_cache_timestamp_name: datetime.datetime.now(),
                    mongo_cache_request_id_name: request_id,
                    mongo_cache_response_name: r
                })

                mongo_collection.insert_one(save_key)
                return mongo_cache_request_and_pack(request_action=request_action,
                                                    is_success=is_success,
                                                    mongo_collection=mongo_collection,
                                                    query=query,
                                                    save_key=save_key,
                                                    fail_action=fail_action,
                                                    mongo_cache_request_id_name=mongo_cache_request_id_name,
                                                    mongo_cache_response_name=mongo_cache_response_name,
                                                    mongo_cache_timestamp_name=mongo_cache_timestamp_name,
                                                    try_times=try_times)
        except Exception as e:
            if fail_action:
                fail_action()

            return mongo_cache_request_and_pack(request_action=request_action,
                                                is_success=is_success,
                                                mongo_collection=mongo_collection,
                                                query=query,
                                                save_key=save_key,
                                                fail_action=fail_action,
                                                mongo_cache_request_id_name=mongo_cache_request_id_name,
                                                mongo_cache_response_name=mongo_cache_response_name,
                                                mongo_cache_timestamp_name=mongo_cache_timestamp_name,
                                                try_times=try_times - 1)
