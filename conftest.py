
def pytest_collection_modifyitems(config, items):
    """
    pytest hook to modify collected items before the execution starts.
    :param items: list of tests collected.
    :return:
    """
    selected_items = []
    if config.option.seq:
        print("Runing test with sequence:")
        cmdopt = config.getoption('customseq')
        seq = cmdopt.split(",")
        print(seq)
        for s in seq:
            for item in items:
                if s in str(item):
                    selected_items.append(item)
        items[:] = selected_items


def pytest_addoption(parser):
    """
    Pytest hook, add support for extra command line options.
    :Param parser: The parser which needs to be modified.
    """
    parser.addoption("--seq", action="store_true", default=False, help="Run tests in sequence order")
    parser.addoption(
        "--customseq", action="store",
        default="test_cloud_delete_all_tenants_v1,test_cloud_configure,test_cloud_wsg_edge,test_cloud_add_cms,test_cloud_admin_add_channel,test_verify_admin_streaming,test_cloud_admin_edit_channel,test_cloud_admin_add_source,test_cloud_admin_edit_source,test_verify_publisher,test_cloud_wsg_settings,test_cloud_change_cms_name,test_verify_audit_wsg,test_cloud_delete_cms,test_teardown",

        # default ="test_cloud_delete_all_tenants_v1,test_cloud_configure,test_cloud_offline_configure_peacebox,test_update_with_file,test_cloud_config_add_peacebox_from_gateway_page,test_cloud_gateway,test_update_xms,test_cloud_settings,test_cloud_devices,test_update_devices,test_cloud_scheduler,test_cloud_dashboard,test_cloud_delete_devices,test_cloud_restore_devices_db,test_cloud_create_new_tenant_configure_xms,test_teardown",

        # default="test_mt,test_sys,test_tb,test_update,test_cloud_gateway,test_cloud_devices,test_cloud_settings,test_cloud_dashboard,test_nw_neg,test_mvgw,test_reset,test_fn_sys,test_fn_login,test_fn_neg_configure,test_shutdown,test_teardown",
        help="Provide Custom test case sequence execution"
    )

