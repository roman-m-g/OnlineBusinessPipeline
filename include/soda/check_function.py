from soda.scan import Scan


def check(scan_name, checks_subpath, data_source='online_business'):
    scan = Scan()
    scan.set_verbose()
    scan.set_scan_definition_name(scan_name)
    scan.set_data_source_name(data_source)
    scan.add_configuration_yaml_file(
        file_path='/usr/local/airflow/include/soda/configuration.yml'
    )
    scan.add_sodacl_yaml_files(
        f'/usr/local/airflow/include/soda/checks/{checks_subpath}'
    )
    result = scan.execute()
    print(scan.get_logs_text())
    if result == 2:
        raise ValueError(f'Soda scan {scan_name!r} failed with errors')
    return result
