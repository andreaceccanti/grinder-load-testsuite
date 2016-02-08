# The Atlas nested test

Each thread creates `atlas_nested.nesting_levels` nested directories into remote `atlas_nested.test_directory`, and upload a file (size = `atlas_nested.file_size_in_bytes`).

The test consists of one srmLs, followed by a srmPtG and a srmRf on file surl.

At the end, each thread cleans its remote file.

## Variables

### Common variables

```
common.storm_dav_endpoint_list = omii006-vm03.cnaf.infn.it:8443
common.storm_fe_endpoint_list = omii006-vm03.cnaf.infn.it:8444
common.test_storagearea = test.vo
```

### Atlas nested load test properties

```
atlas_nested.test_directory = atlas_test
atlas_nested.nesting_levels = 256
atlas_nested.file_size_in_bytes = 10000

atlas_nested.transfer_protocol = https
atlas_nested.sleep_threshold=50
atlas_nested.sleep_time=.5
```
