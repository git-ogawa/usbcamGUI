# logicool

| fourcc | ext | ffmpeg | os | cam | ok | comment |
| :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: |
| YUYV | avi | rawvideo yuyv422 | ng | ubuntu | logi | - |
| XVID | avi | mpeg4 (Simple Profile) (XVID | ok | ubuntu | logi | v4l2のサポート形式には表示されないがうまくいった。
| MP4S | avi | mpeg4 (Simple Profile) (MP4S yuv420p | ok | ubuntu | logi | v4l2のサポート形式には表示されないがうまくいった。|
| MP4S | mp4 | - | ng | ubuntu | logi |  This encoder requires using the avcodec_send_frame() API. のエラーが表示される。outputの中身は空|
| X264 | mp4 / avi | - | ng | ubuntu | logi | Could not find encoder for codec id 27: Encoder not found |
| AVC1 | mp4 / avi | - | ng | ubuntu | logi | Could not find encoder for codec id 27: Encoder not found |


# raspi

| AVC1 | avi | Video: h264 (High) (avc1 / 0x31637661), yuv420p(progressive) | ok | raspi | raspicam | 撮影時はエラーが出ないがファイルが開けない |
| AVC1 | mp4 | Video: h264 (High) (avc1 / 0x31637661), yuv420p(progressive) | ok | raspi | raspicam |  |


