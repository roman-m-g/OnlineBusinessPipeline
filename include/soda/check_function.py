from pathlib import Path

VALID_STAGES = {'sources', 'transform', 'report'}


def check(scan_name, checks_subpath):
    if checks_subpath not in VALID_STAGES:
        raise ValueError(f'Invalid checks_subpath: {checks_subpath!r}')

    from soda_core.contracts.contract_verification import (
        ContractVerificationSession,
        ContractYamlSource,
        DataSourceYamlSource,
    )

    contracts_dir = Path(f'/usr/local/airflow/include/soda/checks/{checks_subpath}')
    config_file = '/usr/local/airflow/include/soda/configuration.yml'

    contract_files = sorted(contracts_dir.glob('*.yml'))
    if not contract_files:
        raise ValueError(f'No contract files found in {contracts_dir}')

    result = ContractVerificationSession.execute(
        contract_yaml_sources=[ContractYamlSource(file_path=str(f)) for f in contract_files],
        data_source_yaml_sources=[DataSourceYamlSource(file_path=config_file)],
    )

    print(result.get_logs_str())

    if not result.is_ok:
        raise ValueError(
            f'Soda contract verification {scan_name!r} failed:\n{result.get_errors_str()}'
        )
