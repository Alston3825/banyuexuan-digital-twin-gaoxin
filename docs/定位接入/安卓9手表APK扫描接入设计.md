# 安卓 9 手表 APK 扫描接入设计 v0.1

**后续核验已找到现有实现**：用户授权读取呼叫定位项目后，确认源码位于 `/Users/alston/Projects/Codex/接手项目/伴月轩智能呼叫定位系统/development/bycall`，已实现 BLE 周期扫描、解析、MQTT 上报及后台参数配置。下文“缺源码”和新模块/新消息为先前阶段草案，不能当作当前缺失功能或直接覆盖原协议。以 [呼叫定位项目对接核验](呼叫定位项目对接核验.md) 的现状及增量差距为准。

依据：用户确认 ZM10 公版手表运行安卓 9，已有自研 APK 与主机、平板连接，手表未连接手机；系统蓝牙列表可见 MBeacon，但尝试配对提示 PIN/密钥错误。用户陈述已登记，APK、SDK 和实机扫描尚未核验。

状态：功能与消息设计完成，当前目录未发现 Android 源码，未编译 APK、未连接手表、未部署服务。待提供现有 APK 源码目录、通信代码和 Gradle/Manifest 后在原工程实施，不另建重复业务系统。

## 1. 连接路线

固定信标广播 → 手表 APK 的 BLE 扫描 → 本地采样汇总 → 现有主机通信通道 → 主机区域判断 → 现有平板/3D 事件分发。

定位扫描不调用 `createBond()`、不输入系统 PIN，也不调用 `connectGatt()`。BeaconSET 的参数修改密码与系统蓝牙配对不是同一个流程，不尝试用配置密码配对。系统列表能看到设备只说明当前能发现它，仍需验证应用能收到 iBeacon 广播内容。

首枚保持现有 UUID/Major/Minor、500 ms 周期、功率原档和校验距离。手机 BeaconSET 完成查看后断开配置连接，再进行手表扫描测试。名称 MBeacon 仅作辅助显示，不作为身份或唯一过滤条件。

## 2. APK 内部职责

- `BeaconScanController`：统一持有扫描器、生命周期与扫描任务，避免 Activity/Service 多处重复启动。状态为 stopped、ready、scanning、waiting、blocked、backoff。
- `BeaconFrameDecoder`：解析广播并校验格式；对照现有信标身份验证 UUID、Major、Minor 和 RSSI。完整 UUID+Major+Minor 作为信标业务键，不用 MAC 绑定员工。
- `ObservationWindow`：以扫描窗口聚合每枚信标的样本数、RSSI 中位数/最小/最大、首末采集时刻，保留本机有限诊断样本。
- `ExistingTransportAdapter`：复用已有连接、设备认证与发送队列。扫描回调不做网络请求，不创建第二条无必要的主机连接。
- 主机端维护“信标身份 → 门店/楼层/房间/安装点”的映射、员工与手表绑定。手表扫描本身不写死楼层，更不能把可见信标位置当作佩戴者精确坐标。

类名是职责建议，收到源码后依工程语言与现有架构调整，不声称这些类已经实现。

## 3. 扫描策略（首轮工程试测值）

|项目|首轮建议|说明|
|---|---|---|
|启停|上岗启动、离岗停止|提供可见的采集中状态与停止入口，不退出页面就误停|
|扫描窗口|5 秒|每次有明确停止期限|
|启动周期|15 秒|扫 5 秒、等待约 10 秒；参数可配，不做失败后紧密重启|
|扫描模式|BALANCED 起步|诊断时可短暂使用 LOW_LATENCY 对照，持续策略以耗电和接收率实测决定|
|结果过滤|有效 iBeacon 广播格式 + 已登记身份白名单|使用有效 ScanFilter，不能只在回调里过滤所有设备；不要用 GATT service UUID 过滤代替 iBeacon 身份解析|
|上报|每个完成窗口一条汇总|保留窗口时间及状态，空结果也有意义|

15 秒周期意味着窗口之间有空档，不承诺秒级到达提示；需更低时延时，调整采集策略并复测电量/后台行为，不能把 500 ms 广播周期当作定位刷新周期。

BLE API 使用 `BluetoothLeScanner.startScan(filters, settings, callback)` 与对应 `stopScan(callback)`；同一控制器串行修改状态，处理批量结果、迟到回调和 `onScanFailed`。扫描窗口携带 generation/windowId，停止后的旧回调不得混入新窗口。

扫描前检测 BLE 硬件特性、蓝牙开关、权限、定位服务状态；不满足时上报具体 blocked 原因，禁止静默生成“附近无人”。扫描失败记录错误码并退避；蓝牙重开/权限恢复后只重启一次有效任务，停止/离岗时取消定时器并释放回调。

## 4. 安卓 9 权限与锁屏运行

Manifest 合并原则：在现有清单中核对 `BLUETOOTH`、`BLUETOOTH_ADMIN`、`ACCESS_FINE_LOCATION`，联网通道沿用已有 `INTERNET`；前台服务按 targetSdk 核对 `FOREGROUND_SERVICE`。位置权限须运行时申请，安卓 9 同时核对定位总开关。此处只描述 Android 9 路径；不因为设备运行安卓 9 就擅自降 targetSdk。若原 APK 兼容其他系统，保留对应版本分支。

持续值班采集优先复用现有前台服务，或增加带通知渠道与常驻通知的采集服务；按系统要求及时 `startForeground()`。不能只依靠 Activity、短周期 WorkManager 或声称前台服务能保证永不休眠。若现有 APK 已有采集/长连接服务，先评估合并职责。

官方 API 指出未过滤扫描会在熄屏时停止；需使用真实匹配的 ScanFilter 并实测手表固件的过滤支持。不能仅在界面亮屏下验收。短窗口调度在休眠时可能延迟，实际记录计划/执行时间、窗口有效时长、锁屏漏报和唤醒情况；若不满足值班刷新要求，再结合源码评估受控唤醒或其他扫描调度方案。

以上不需要先连接手机或配对信标；原主机链路若使用蓝牙，要另外验证并发扫描对原业务连接、消息时延和稳定性的影响。

## 5. 手表至主机候选消息

与 `接口契约v0.1.md` 的 observation 分支衔接。传输协议及外层认证沿用原工程，下例是虚构载荷，不是已部署接口。

```json
{
  "schemaVersion": "0.1",
  "type": "beacon.observation.window",
  "eventId": "example-session-1:12",
  "deviceId": "watch-example-001",
  "streamId": "example-session-1",
  "sequence": 12,
  "window": {
    "startedAt": "2026-11-20T10:00:00Z",
    "endedAt": "2026-11-20T10:00:05Z",
    "startedElapsedMs": 100000,
    "endedElapsedMs": 105000,
    "status": "completed",
    "scannerErrorCode": null,
    "timeQuality": "device_wall_clock_unverified"
  },
  "observations": [
    {
      "uuid": "00000000-0000-0000-0000-000000000001",
      "major": 24,
      "minor": 1,
      "sampleCount": 8,
      "rssiMedianDbm": -65,
      "rssiMinDbm": -72,
      "rssiMaxDbm": -61,
      "lastSeenElapsedMs": 104800
    }
  ]
}
```

主机登记 `receivedAt`；单调时间用于窗口时长与样本新鲜度，不跨重启比较。源序号在同一 streamId 内递增，重启生成新 streamId。重发保持 eventId 不变以便去重。接收端校验负 RSSI/数值范围、UUID、样本数、时间顺序、体积、认证设备及信标映射，异常进入诊断，不直接更新定位。

正常完成但未发现目标时发送 `completed` 且 observations 为空；权限/蓝牙关闭或异常分别发送 blocked/failed 及结构化原因，不冒充一次正常空扫描。部分窗口异常时不使用它确认离开房间。

传输中断使用有限队列，建议首轮上限 100 个窗口或 30 分钟（先到者淘汰）；实际沿用现有可靠队列并记录丢弃数。恢复后历史窗口标记 replay，只供历史与诊断，不覆盖主机较新的当前状态。实时状态优先重新采集同步，不把积压位置当成刚发生。

## 6. 主机区域判断及 3D

首期采用区域定位。维护候选区域、已确认区域、最后可信时间和 unknown/stale；结合窗口 RSSI 中位数、邻房差值、最少样本和连续窗口确认来抑制抖动。上述阈值应通过 2414/2415 门内外实测选择，不以一次最强信号直接判定房间。

楼层同样由经核对的映射及有效观测判断；跨楼层接收到信号时不盲目切换。多窗口无可信观测后进入 unknown/stale，阈值待现场确定。3D 展示房间归属/约定展示点，不宣称人体连续坐标；过期时停止位置动画并显示更新时间，不调用现有模拟任务来补轨迹。

## 7. 首轮联调完成条件

1. APK 在测试页输出当前信标真实 UUID/Major/Minor、RSSI 和采集时间，与手机记录一致；无 PIN 或 GATT 配对步骤。
2. 主机通过原链路收到完成/空/blocked/failed 窗口，唯一键去重、断网重发、恢复实时状态正确。
3. 在亮屏、熄屏、返回桌面及原业务运行时连续验证；记录实际采集间隔、覆盖、耗电和原连接稳定性。
4. 蓝牙关闭重开、权限拒绝/恢复、离岗停止、进程重启、主机离线均有明确状态；不能把扫描失败当作离开房间。
5. 2414/2415、护理站和走廊完成区域混淆/切换延迟记录，再接入 3D。未通过以上测试不标记为实机定位完成。

## 官方技术依据

- [BLE 发现与扫描 API](https://developer.android.com/develop/connectivity/bluetooth/ble/find-ble-devices)：限时扫描、回调与过滤。
- [蓝牙权限](https://developer.android.com/develop/connectivity/bluetooth/bt-permissions)：旧版系统权限及运行时位置授权。
- [BluetoothLeScanner](https://developer.android.com/reference/android/bluetooth/le/BluetoothLeScanner)：熄屏时无过滤扫描的行为。
- [Android 9 target 28 行为变化](https://developer.android.com/about/versions/pie/android-9.0-changes-28)：前台服务权限。
