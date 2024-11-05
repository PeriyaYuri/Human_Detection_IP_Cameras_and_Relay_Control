import RtspFFmpeg from 'rtsp-ffmpeg';

export class CameraHandler {
  constructor(url) {
    this.url = url;
    this.stream = null;
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.stream = new RtspFFmpeg({
          input: this.url,
          rate: 10
        });
        
        this.stream.on('start', () => {
          resolve(true);
        });

        this.stream.on('error', (err) => {
          reject(err);
        });
      } catch (err) {
        reject(err);
      }
    });
  }

  readFrame() {
    return new Promise((resolve) => {
      if (!this.stream) {
        resolve(null);
        return;
      }

      this.stream.on('data', (frame) => {
        resolve(frame);
      });
    });
  }

  addTimestamp(frame) {
    const now = new Date().toISOString();
    frame.putText(
      now,
      [10, frame.height() - 10],
      'Arial',
      0.5,
      [255, 255, 255],
      1
    );
  }

  release() {
    if (this.stream) {
      this.stream.stop();
      this.stream = null;
    }
  }
}