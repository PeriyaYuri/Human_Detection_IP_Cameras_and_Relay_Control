import { HumanDetector } from './detector.js';
import { RelayController } from './gpio-controller.js';
import { CameraHandler } from './camera-handler.js';

export class CameraSystem {
  constructor() {
    this.detector = new HumanDetector();
    this.relayController = new RelayController(17, 18, 5);
    
    this.cameraUrls = [
      'rtsp://username:password@camera1_ip:554/stream1',
      'rtsp://username:password@camera2_ip:554/stream2'
    ];

    this.detectionZones = [
      [[100, 100], [500, 400]],
      [[100, 100], [500, 400]]
    ];

    this.cameras = this.cameraUrls.map(url => new CameraHandler(url));
    this.frames = [null, null];
    this.running = true;
  }

  async setupCamera(cameraIndex) {
    while (this.running) {
      try {
        await this.cameras[cameraIndex].connect();
        break;
      } catch (err) {
        console.error(`Camera ${cameraIndex + 1} connection error:`, err);
        await new Promise(resolve => setTimeout(resolve, 5000));
      }
    }
  }

  async processCamera(cameraIndex) {
    const camera = this.cameras[cameraIndex];
    const zone = this.detectionZones[cameraIndex];

    while (this.running) {
      try {
        const frame = await camera.readFrame();
        if (!frame) {
          await new Promise(resolve => setTimeout(resolve, 1000));
          continue;
        }

        // Draw detection zone
        frame.rectangle(zone[0], zone[1], [0, 255, 0], 2);

        // Detect humans
        const boxes = await this.detector.detectHumans(frame, zone);

        if (boxes.length > 0) {
          frame.putText(
            `Person Detected - Camera ${cameraIndex + 1}`,
            [10, 30],
            'Arial',
            1,
            [0, 0, 255],
            2
          );

          this.relayController.activateRelay(cameraIndex);
          this.detector.drawDetections(frame, boxes, zone);
        }

        camera.addTimestamp(frame);
        this.frames[cameraIndex] = frame;

      } catch (err) {
        console.error(`Error processing camera ${cameraIndex + 1}:`, err);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }
  }

  async run() {
    try {
      // Setup cameras
      await Promise.all(
        this.cameras.map((_, index) => this.setupCamera(index))
      );

      // Process cameras
      await Promise.all(
        this.cameras.map((_, index) => this.processCamera(index))
      );

    } catch (err) {
      console.error('System error:', err);
    } finally {
      this.cleanup();
    }
  }

  cleanup() {
    this.running = false;
    this.cameras.forEach(camera => camera.release());
    this.relayController.cleanup();
  }
}