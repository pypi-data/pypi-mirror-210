def get_model_object(calling_obj, error_model, model, pk_value):
    if calling_obj is None or error_model is None or model is None or pk_value is None or str(pk_value) == 'nan':
        return None
    try:
        return model.objects.get(pk=pk_value) or None
    except model.DoesNotExist as ex:
        kwargs = {
            'source_table': calling_obj.source_table,
            'target_table': calling_obj.target_table,
            'error_row': pk_value,
            'error_message': ex
        }
        error_model.objects.create(**kwargs)
        pass
    return None
