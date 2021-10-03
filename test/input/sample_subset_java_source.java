                @CddTest(requirement="7.8.2.2/H-2-1,H-3-1,H-4-2,H-4-3,H-4-4,H-4-5")
public class USBAudioPeripheralNotificationsTest extends PassFailButtons.Activity {


    @CddTest(requirement="5.1.3")
    public void testDecodeOpusChannelsAndRates() throws Exception {
        String[] mimetypes = { MediaFormat.MIMETYPE_AUDIO_OPUS };
        int[] sampleRates = { 8000, 12000, 16000, 24000, 48000 };
        int[] channelMasks = { AudioFormat.CHANNEL_OUT_MONO,
                               AudioFormat.CHANNEL_OUT_STEREO,
                               AudioFormat.CHANNEL_OUT_5POINT1 };

        verifyChannelsAndRates(mimetypes, sampleRates, channelMasks);
    }

    private void verifyChannelsAndRates(String[] mimetypes, int[] sampleRates,
                                       int[] channelMasks) throws Exception {

        if (!MediaUtils.check(mIsAtLeastR, "test invalid before Android 11")) return;

        for (String mimetype : mimetypes) {
            // ensure we find a codec for all listed mime/channel/rate combinations
            MediaCodecList mcl = new MediaCodecList(MediaCodecList.ALL_CODECS);
            for (int sampleRate : sampleRates) {
                for (int channelMask : channelMasks) {
                    int channelCount = AudioFormat.channelCountFromOutChannelMask(channelMask);
                    MediaFormat desiredFormat = MediaFormat.createAudioFormat(
                                mimetype,
                                sampleRate,
                                channelCount);
                    String codecname = mcl.findDecoderForFormat(desiredFormat);

                    assertTrue("findDecoderForFormat() failed for mime=" + mimetype
                               + " sampleRate=" + sampleRate + " channelCount=" + channelCount,
                               codecname != null);
                }
            }


                skipped = false;
                boolean found = false;
                for (int c : caps.colorFormats) {
                    if (c == caps.COLOR_FormatYUV420Flexible) {
                        found = true;
                        break;
                    }
                }
                assertTrue(
                    info.getName() + " does not advertise COLOR_FormatYUV420Flexible",
                    found);

                MediaCodec codec = null;
                MediaFormat format = null;