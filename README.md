# Pervus Bluepad32 Test
SP526 / ESP32-S3 BLE disconnect diagnostic build.

Upload this ZIP's contents to the root of `Pervus-Bluepad32-Test`, then run **Actions > Build patched Bluepad32 S3 diagnostic > Run workflow**.

Stage 1:
- Bluepad32 Arduino template 4.1.0
- ESP32-S3
- invalid `hids_cid` guard
- duplicate-advertisement + pairing lifecycle logs
- NO stale-device deletion/replacement yet
