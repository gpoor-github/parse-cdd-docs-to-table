## 2.2\. Handheld Requirements

An **Android Handheld device** refers to an Android device implementation that is
typically used by holding it in the hand, such as an mp3 player, phone, or
tablet.

Android device implementations are classified as a Handheld if they meet all the
following criteria:

*   Have a power source that provides mobility, such as a battery.
*   Have a physical diagonal screen size in the range of 3.3 inches (or
    2.5 inches for devices which launched on an API level earlier than
    Android 11) to 8 inches.

The additional requirements in the rest of this section are specific to Android
Handheld device implementations.


<div class="note">
<b>Note:</b> Requirements that do not apply to Android Tablet devices are marked with an *.
</div>

### 2.2.1\. Hardware

Handheld device implementations:

*   [[7.1](#7_1_display_and_graphics).1.1/H-0-1] MUST have at least one
Android-compatible display that meets all requirements described on this
document.
*   [[7.1](#7_1_display_and_graphics).1.3/H-SR] Are STRONGLY RECOMMENDED to
provide users an affordance to change the display size (screen density).

If Handheld device implementations support software screen rotation, they:

*   [[7.1](#7_1_display_and_graphics).1.1/H-1-1]* MUST make the logical screen
that is made available for third party applications be at least 2 inches on the
short edge(s) and 2.7 inches on the long edge(s).
Devices which launched on an API level earlier than that of this document are
exempted from this requirement.

If Handheld device implementations do not support software screen rotation,
they:

*   [[7.1](#7_1_display_and_graphics).1.1/H-2-1]* MUST make the logical screen
that is made available for third party applications be at least 2.7 inches on
the short edge(s).
Devices which launched on an API level earlier than that of this document are
exempted from this requirement.

If Handheld device implementations claim support for high dynamic range
displays through [`Configuration.isScreenHdr()`
](https://developer.android.com/reference/android/content/res/Configuration.html#isScreenHdr%28%29)
, they:

*   [[7.1](#7_1_display-and-graphics).4.5/H-1-1] MUST advertise support for the
    `EGL_EXT_gl_colorspace_bt2020_pq`, `EGL_EXT_surface_SMPTE2086_metadata`,
    `EGL_EXT_surface_CTA861_3_metadata`, `VK_EXT_swapchain_colorspace`, and
    `VK_EXT_hdr_metadata` extensions.

Handheld device implementations:

*   [[7.1](#7_1_display_and_graphics).4.6/H-0-1] MUST report whether the device
    supports the GPU profiling capability via a system property
    `graphics.gpu.profiler.support`.

If Handheld device implementations declare support via a system property
`graphics.gpu.profiler.support`, they:

*    [[7.1](#7_1_display_and_graphics).4.6/H-1-1] MUST report as output a
     protobuf trace that complies with the schema for GPU counters and GPU
     renderstages defined in the [Perfetto documentation](https://developer.android.com/studio/command-line/perfetto).
*    [[7.1](#7_1_display_and_graphics).4.6/H-1-2] MUST report conformant values
     for the device’s GPU counters following the
     [gpu counter trace packet proto](https://android.googlesource.com/platform/external/perfetto/+/refs/heads/master/protos/perfetto/trace/gpu/gpu_counter_event.proto).
*    [[7.1](#7_1_display_and_graphics).4.6/H-1-3] MUST report conformant values
     for the device’s GPU RenderStages following the
     [render stage trace packet proto](https://android.googlesource.com/platform/external/perfetto/+/refs/heads/master/protos/perfetto/trace/gpu/gpu_render_stage_event.proto).
*    [[7.1](#7_1_display_and_graphics).4.6/H-1-4] MUST report a GPU Frequency
     tracepoint as specified by the format: [power/gpu_frequency](https://android.googlesource.com/platform/external/perfetto/+/refs/heads/master/protos/perfetto/trace/ftrace/power.proto).

Handheld device implementations:

*   [[7.1](#7_1_display_and_graphics).5/H-0-1] MUST include support for legacy
application compatibility mode as implemented by the upstream Android open
source code. That is, device implementations MUST NOT alter the triggers or
thresholds at which compatibility mode is activated, and MUST NOT alter the
behavior of the compatibility mode itself.
*   [[7.2](#7_2_input_devices).1/H-0-1] MUST include support for third-party
Input Method Editor (IME) applications.
*   [[7.2](#7_2_input_devices).3/H-0-3] MUST provide the Home function on
    all the Android-compatible displays that provide the home screen.
*   [[7.2](#7_2_input_devices).3/H-0-4] MUST provide the Back function on all
    the Android-compatible displays and the Recents function on at least one of
    the Android-compatible displays.
*   [[7.2](#7_2_input_devices).3/H-0-2] MUST send both the normal and long press
event of the Back function ([`KEYCODE_BACK`](
http://developer.android.com/reference/android/view/KeyEvent.html#KEYCODE_BACK))
to the foreground application. These events MUST NOT be consumed by the system
and CAN be triggered by outside of the Android device (e.g. external hardware
keyboard connected to the Android device).
*   [[7.2](#7_2_input_devices).4/H-0-1] MUST support touchscreen input.
*   [[7.2](#7_2_input_devices).4/H-SR] Are STRONGLY RECOMMENDED to launch the
user-selected assist app, in other words the app that implements
VoiceInteractionService, or an activity handling the [`ACTION_ASSIST`](https://developer.android.com/reference/android/content/Intent#ACTION_ASSIST)
on long-press of [`KEYCODE_MEDIA_PLAY_PAUSE`](https://developer.android.com/reference/android/view/KeyEvent#KEYCODE_MEDIA_PLAY_PAUSE)
or [`KEYCODE_HEADSETHOOK`](https://developer.android.com/reference/android/view/KeyEvent#KEYCODE_HEADSETHOOK)
if the foreground activity does not handle those long-press events.
*  [[7.3](#7_3_sensors).1/H-SR] Are STRONGLY RECOMMENDED to include a 3-axis
accelerometer.

If Handheld device implementations include a 3-axis accelerometer, they:

*  [[7.3](#7_3_sensors).1/H-1-1] MUST be able to report events up to a frequency
of at least 100 Hz.

If Handheld device implementations include a GPS/GNSS receiver and report the
capability to applications through the `android.hardware.location.gps` feature
flag, they:

*  [[7.3](#7_3_sensors).3/H-2-1] MUST report GNSS measurements, as soon as they
are found, even if a location calculated from GPS/GNSS is not yet reported.
*  [[7.3](#7_3_sensors).3/H-2-2] MUST report GNSS pseudoranges and pseudorange
rates, that, in open-sky conditions after determining the location, while
stationary or moving with less than 0.2 meter per second squared of
acceleration, are sufficient to calculate position within 20 meters, and speed
within 0.2 meters per second, at least 95% of the time.

If Handheld device implementations include a 3-axis gyroscope, they:

*  [[7.3](#7_3_sensors).4/H-3-1] MUST be able to report events up to a frequency
of at least 100 Hz.
*  [[7.3](#7_3_sensors).4/H-3-2] MUST be capable of measuring orientation changes
up to 1000 degrees per second.

Handheld device implementations that can make a voice call and indicate
any value other than `PHONE_TYPE_NONE` in `getPhoneType`:

*  [[7.3](#7_3_sensors).8/H] SHOULD include a proximity sensor.

Handheld device implementations:

*  [[7.3](#7_3_sensors).11/H-SR] Are RECOMMENDED to support pose sensor with 6
degrees of freedom.
*  [[7.4](#7_4_data_connectivity).3/H] SHOULD include support for Bluetooth and
Bluetooth LE.

If Handheld device implementations include a metered connection, they:

*  [[7.4](#7_4_data_connectivity).7/H-1-1] MUST provide the data saver mode.

If Handheld device implementations include a logical camera device that lists
capabilities using
[`CameraMetadata.REQUEST_AVAILABLE_CAPABILITIES_LOGICAL_MULTI_CAMERA`](
https://developer.android.com/reference/android/hardware/camera2/CameraMetadata#REQUEST_AVAILABLE_CAPABILITIES_LOGICAL_MULTI_CAMERA),
they:

*   [[7.5](#7_5_camera).4/H-1-1] MUST have normal field of view (FOV) by default
    and it MUST be between 50 and 90 degrees.

Handheld device implementations:

*  [[7.6](#7_6_memory_and_storage).1/H-0-1] MUST have at least 4 GB of
non-volatile storage available for application private data
(a.k.a. "/data" partition).
*  [[7.6](#7_6_memory_and_storage).1/H-0-2] MUST return “true” for
`ActivityManager.isLowRamDevice()` when there is less than 1GB of memory
available to the kernel and userspace.

If Handheld device implementations declare support of only a 32-bit ABI:

*   [[7.6](#7_6_memory_and_storage).1/H-1-1] The memory available to the kernel
    and userspace MUST be at least 416MB if the default display uses framebuffer
    resolutions up to qHD (e.g. FWVGA).

*   [[7.6](#7_6_memory_and_storage).1/H-2-1] The memory available to the kernel
    and userspace MUST be at least 592MB if the default display uses framebuffer
    resolutions up to HD+ (e.g. HD, WSVGA).

*   [[7.6](#7_6_memory_and_storage).1/H-3-1] The memory available to the kernel
    and userspace MUST be at least 896MB if the default display uses framebuffer
    resolutions up to FHD (e.g. WSXGA+).

*   [[7.6](#7_6_memory_and_storage).1/H-4-1] The memory available to the kernel
    and userspace MUST be at least 1344MB if the default display uses
    framebuffer resolutions up to QHD (e.g. QWXGA).

If Handheld device implementations declare support of 32-bit and 64-bit ABIs:

*   [[7.6](#7_6_memory_and_storage).1/H-5-1] The memory available to the kernel
    and userspace MUST
    be at least 816MB if the default display uses framebuffer resolutions up
    to qHD (e.g. FWVGA).

*   [[7.6](#7_6_memory_and_storage).1/H-6-1] The memory available to the kernel
    and userspace MUST be at least
    944MB if the default display uses framebuffer resolutions up to HD+
    (e.g. HD, WSVGA).

*   [[7.6](#7_6_memory_and_storage).1/H-7-1] The memory available to the kernel
    and userspace MUST be at least
    1280MB if the default display uses framebuffer resolutions up to FHD
    (e.g. WSXGA+).

*   [[7.6](#7_6_memory_and_storage).1/H-8-1] The memory available to the kernel
    and userspace MUST be at least
    1824MB if the default display uses framebuffer resolutions up to QHD
    (e.g. QWXGA).

Note that the "memory available to the kernel and userspace" above refers to the
memory space provided in addition to any memory already dedicated to hardware
components such as radio, video, and so on that are not under the kernel’s
control on device implementations.

If Handheld device implementations include less than or equal to 1GB of memory
available to the kernel and userspace, they:

*   [[7.6](#7_6_memory-and-storage).1/H-9-1] MUST declare the feature flag
    [`android.hardware.ram.low`](
    https://developer.android.com/reference/android/content/pm/PackageManager.html#FEATURE_RAM_LOW).
*   [[7.6](#7_6_memory-and-storage).1/H-9-2] MUST have at least 1.1 GB of
    non-volatile storage for application
    private data (a.k.a. "/data" partition).

If Handheld device implementations include more than 1GB of memory available
to the kernel and userspace, they:

*   [[7.6](#7_6_memory-and-storage).1/H-10-1] MUST have at least 4GB of
    non-volatile storage available for
    application private data (a.k.a. "/data" partition).
*   SHOULD declare the feature flag [`android.hardware.ram.normal`](
    https://developer.android.com/reference/android/content/pm/PackageManager.html#FEATURE_RAM_NORMAL).

Handheld device implementations:

*   [[7.6](#7_6_memory_and_storage).2/H-0-1] MUST NOT provide an application
shared storage smaller than 1 GiB.
*   [[7.7](#7_7_usb).1/H] SHOULD include a USB port supporting peripheral mode.

If handheld device implementations include a USB port supporting peripheral
mode, they:

*   [[7.7](#7_7_usb).1/H-1-1] MUST implement the Android Open Accessory (AOA)
API.

If Handheld device implementations include a USB port supporting host mode,
they:

*   [[7.7](#7_7_usb).2/H-1-1] MUST implement the [USB audio class](
http://developer.android.com/reference/android/hardware/usb/UsbConstants.html#USB_CLASS_AUDIO)
as documented in the Android SDK documentation.

Handheld device implementations:

*   [[7.8](#7_8_audio).1/H-0-1] MUST include a microphone.
*   [[7.8](#7_8_audio).2/H-0-1] MUST have an audio output and declare
`android.hardware.audio.output`.

If Handheld device implementations are capable of meeting all the performance
requirements for supporting VR mode and include support for it, they:

*   [[7.9](#7_9_virtual_reality).1/H-1-1] MUST declare the
`android.hardware.vr.high_performance` feature flag.
*   [[7.9](#7_9_virtual_reality).1/H-1-2] MUST include an application
implementing `android.service.vr.VrListenerService` that can be enabled by VR
applications via `android.app.Activity#setVrModeEnabled`.

If Handheld device implementations include one or more USB-C port(s) in host
mode and implement (USB audio class), in addition to requirements in
[section 7.7.2](#7_7_2_USB_host_mode), they:

*    [[7.8](#7_8_audio).2.2/H-1-1] MUST provide the following software mapping
of HID codes:

<table>
  <tr>
   <th>Function</th>
   <th>Mappings</th>
   <th>Context</th>
   <th>Behavior</th>
  </tr>
  <tr>
   <td rowspan="6">A</td>
   <td rowspan="6"><strong>HID usage page</strong>: 0x0C<br>
       <strong>HID usage</strong>: 0x0CD<br>
       <strong>Kernel key</strong>: <code>KEY_PLAYPAUSE</code><br>
       <strong>Android key</strong>: <code>KEYCODE_MEDIA_PLAY_PAUSE</code></td>
   <td rowspan="2">Media playback</td>
   <td><strong>Input</strong>: Short press<br>
       <strong>Output</strong>: Play or pause</td>
  </tr>
  <tr>
   <td><strong>Input</strong>: Long press<br>
       <strong>Output</strong>: Launch voice command<br>
       <strong>Sends</strong>:
       <code>android.speech.action.VOICE_SEARCH_HANDS_FREE</code> if the device
       is locked or its screen is off. Sends
       <code>android.speech.RecognizerIntent.ACTION_WEB_SEARCH</code> otherwise</td>
  </tr>
  <tr>
   <td rowspan="2">Incoming call</td>
   <td><strong>Input</strong>: Short press<br>
       <strong>Output</strong>: Accept call</td>
  </tr>
  <tr>
   <td><strong>Input</strong>: Long press<br>
       <strong>Output</strong>: Reject call</td>
  </tr>
  <tr>
   <td rowspan="2">Ongoing call</td>
   <td><strong>Input</strong>: Short press<br>
       <strong>Output</strong>: End call</td>
  </tr>
  <tr>
   <td><strong>Input</strong>: Long press<br>
       <strong>Output</strong>: Mute or unmute microphone</td>
  </tr>
  <tr>
   <td>B</td>
   <td><strong>HID usage page</strong>: 0x0C<br>
       <strong>HID usage</strong>: 0x0E9<br>
       <strong>Kernel key</strong>: <code>KEY_VOLUMEUP</code><br>
       <strong>Android key</strong>: <code>VOLUME_UP</code></td>
   <td>Media playback, Ongoing call</td>
   <td><strong>Input</strong>: Short or long press<br>
       <strong>Output</strong>: Increases the system or headset volume</td>
  </tr>
  <tr>
   <td>C</td>
   <td><strong>HID usage page</strong>: 0x0C<br>
       <strong>HID usage</strong>: 0x0EA<br>
       <strong>Kernel key</strong>: <code>KEY_VOLUMEDOWN</code><br>
       <strong>Android key</strong>: <code>VOLUME_DOWN</code></td>
   <td>Media playback, Ongoing call</td>
   <td><strong>Input</strong>: Short or long press<br>
       <strong>Output</strong>: Decreases the system or headset volume</td>
  </tr>
  <tr>
   <td>D</td>
   <td><strong>HID usage page</strong>: 0x0C<br>
       <strong>HID usage</strong>: 0x0CF<br>
       <strong>Kernel key</strong>: <code>KEY_VOICECOMMAND</code><br>
       <strong>Android key</strong>: <code>KEYCODE_VOICE_ASSIST</code></td>
   <td>All. Can be triggered in any instance.</td>
   <td><strong>Input</strong>: Short or long press<br>
       <strong>Output</strong>: Launch voice command</td>
  </tr>
</table>

*    [[7.8](#7_8_audio).2.2/H-1-2] MUST trigger [ACTION_HEADSET_PLUG](https://developer.android.com/reference/android/content/Intent#ACTION_HEADSET_PLUG)
upon a plug insert, but only after the USB audio interfaces and endpoints have
been properly enumerated in order to identify the type of terminal connected.

When the USB audio terminal types 0x0302 is detected, they:

*    [[7.8](#7_8_audio).2.2/H-2-1] MUST broadcast Intent ACTION_HEADSET_PLUG with
"microphone" extra set to 0.

When the USB audio terminal types 0x0402 is detected, they:

*    [[7.8](#7_8_audio).2.2/H-3-1] MUST broadcast Intent ACTION_HEADSET_PLUG with
"microphone" extra set to 1.

When API AudioManager.getDevices() is called while the USB peripheral is
connected they:

*    [[7.8](#7_8_audio).2.2/H-4-1] MUST list a device of type [AudioDeviceInfo.TYPE_USB_HEADSET](https://developer.android.com/reference/android/media/AudioDeviceInfo#TYPE_USB_HEADSET)
and role isSink() if the USB audio terminal type field is 0x0302.

*    [[7.8](#7_8_audio).2.2/H-4-2] MUST list a device of type
AudioDeviceInfo.TYPE_USB_HEADSET and role isSink() if the USB audio terminal
type field is 0x0402.

*    [[7.8](#7_8_audio).2.2/H-4-3] MUST list a device of type
AudioDeviceInfo.TYPE_USB_HEADSET and role isSource() if the USB audio terminal
type field is 0x0402.

*    [[7.8](#7_8_audio).2.2/H-4-4] MUST list a device of type [AudioDeviceInfo.TYPE_USB_DEVICE](
https://developer.android.com/reference/android/media/AudioDeviceInfo#TYPE_USB_DEVICE)
and role isSink() if the USB audio terminal type field is 0x603.

*    [[7.8](#7_8_audio).2.2/H-4-5] MUST list a device of type
AudioDeviceInfo.TYPE_USB_DEVICE and role isSource() if the USB audio terminal
type field is 0x604.

*    [[7.8](#7_8_audio).2.2/H-4-6] MUST list a device of type
AudioDeviceInfo.TYPE_USB_DEVICE and role isSink() if the USB audio terminal type
field is 0x400.

*    [[7.8](#7_8_audio).2.2/H-4-7] MUST list a device of type
AudioDeviceInfo.TYPE_USB_DEVICE and role isSource() if the USB audio terminal
type field is 0x400.

*    [[7.8](#7_8_audio).2.2/H-SR] Are STRONGLY RECOMMENDED upon connection of a
USB-C audio peripheral, to perform enumeration of USB descriptors, identify
terminal types and broadcast Intent ACTION_HEADSET_PLUG in less than
1000 milliseconds.

If Handheld device implementations include at least one haptic actuator, they:

*   [[7.10](#7_10_haptics)/H-SR]* Are STRONGLY RECOMMENDED NOT to use an
    eccentric rotating mass (ERM) haptic actuator(vibrator).
*   [[7.10](#7_10_haptics)/H]* SHOULD position the placement of the actuator
    near the location where the device is typically held or touched by hands.
*   [[7.10](#7_10_haptics)/H-SR]* Are STRONGLY RECOMMENDED to implement all
    public constants for [clear haptics](https://source.android.com/devices/haptics)
    in [android.view.HapticFeedbackConstants](https://developer.android.com/reference/android/view/HapticFeedbackConstants#constants)
    namely (CLOCK_TICK, CONTEXT_CLICK, KEYBOARD_PRESS, KEYBOARD_RELEASE,
    KEYBOARD_TAP, LONG_PRESS, TEXT_HANDLE_MOVE, VIRTUAL_KEY,
    VIRTUAL_KEY_RELEASE, CONFIRM, REJECT, GESTURE_START and GESTURE_END).
*   [[7.10](#7_10_haptics)/H-SR]* Are STRONGLY RECOMMENDED to implement all
    public constants for [clear haptics](https://source.android.com/devices/haptics)
    in [android.os.VibrationEffect](https://developer.android.com/reference/android/os/VibrationEffect)
    namely (EFFECT_TICK, EFFECT_CLICK, EFFECT_HEAVY_CLICK and
    EFFECT_DOUBLE_CLICK) and all public constants for [rich haptics](https://source.android.com/devices/haptics)
    in [android.os.VibrationEffect.Composition](https://developer.android.com/reference/android/os/VibrationEffect.Composition)
    namely (PRIMITIVE_CLICK and PRIMITIVE_TICK).
*   [[7.10](#7_10_haptics)/H-SR]* Are STRONGLY RECOMMENDED to use these linked
    haptic constants [mappings](https://source.android.com/devices/haptics).
*   [[7.10](#7_10_haptics)/H-SR]* Are STRONGLY RECOMMENDED to follow
    [quality assessment](https://source.android.com/devices/haptics)
    for [createOneShot()](https://developer.android.com/reference/android/os/VibrationEffect#createOneShot%28long,%20int%29)
    and [createWaveform()](https://developer.android.com/reference/android/os/VibrationEffect#createOneShot%28long,%20int%29)
    API's.
*   [[7.10](#7_10_haptics)/H-SR]* Are STRONGLY RECOMMENDED to verify the
    capabilities for amplitude scalability by running
    [android.os.Vibrator.hasAmplitudeControl()](https://developer.android.com/reference/android/os/Vibrator#hasAmplitudeControl%28%29).

Linear resonant actuator (LRA) is a single mass spring system which has a
dominant resonant frequency where the mass translates in the direction of
desired motion.

If Handheld device implementations include at least one linear resonant
actuator, they:

*  [[7.10](#7_10_haptics)/H]* SHOULD move the haptic actuator in the X-axis of
   portrait orientation.

If Handheld device implementations have a haptic actuator which is X-axis
Linear resonant actuator (LRA), they:

*   [[7.10](#7_10_haptics)/H-SR]* Are STRONGLY RECOMMENDED to have the resonant
    frequency of the X-axis LRA be under 200 Hz.

If handheld device implementations follow haptic constants mapping, they:

*   [[7.10](#7_10_haptics)/H-SR]* Are STRONGLY RECOMMENDED to perform a
    [quality assessment](https://source.android.com/devices/haptics)
    for haptic constants.

### 2.2.2\. Multimedia

Handheld device implementations MUST support the following audio encoding and
decoding formats and make them available to third-party applications:

*    [[5.1](#5_1_media_codecs)/H-0-1] AMR-NB
*    [[5.1](#5_1_media_codecs)/H-0-2] AMR-WB
*    [[5.1](#5_1_media_codecs)/H-0-3] MPEG-4 AAC Profile (AAC LC)
*    [[5.1](#5_1_media_codecs)/H-0-4] MPEG-4 HE AAC Profile (AAC+)
*    [[5.1](#5_1_media-codecs)/H-0-5] AAC ELD (enhanced low delay AAC)

Handheld device implementations MUST support the following video encoding
formats and make them available to third-party applications:

*    [[5.2](#5_2_video_encoding)/H-0-1] H.264 AVC
*    [[5.2](#5_2_video_encoding)/H-0-2] VP8

Handheld device implementations MUST support the following video decoding
formats and make them available to third-party applications:

*    [[5.3](#5_3_video_decoding)/H-0-1] H.264 AVC
*    [[5.3](#5_3_video_decoding)/H-0-2] H.265 HEVC
*    [[5.3](#5_3_video_decoding)/H-0-3] MPEG-4 SP
*    [[5.3](#5_3_video_decoding)/H-0-4] VP8
*    [[5.3](#5_3_video_decoding)/H-0-5] VP9

### 2.2.3\. Software

Handheld device implementations:

*   [[3.2.3.1](#3_2_3_1_common_application_intents)/H-0-1] MUST have an
application that handles the [`ACTION_GET_CONTENT`](