import * as tf from '@tensorflow/tfjs-node';
import cv from 'node-opencv';

export class HumanDetector {
  constructor() {
    this.model = null;
    this.loadModel();
  }

  async loadModel() {
    this.model = await tf.loadGraphModel('https://tfhub.dev/tensorflow/tfjs-model/ssd_mobilenet_v2/1/default/1');
  }

  async detectHumans(frame, zone) {
    if (!this.model) return [];

    // Extract region of interest
    const roi = frame.roi(zone[0][1], zone[1][1], zone[0][0], zone[1][0]);
    
    // Convert to tensor
    const tensor = tf.browser.fromPixels(roi)
      .expandDims()
      .toFloat();

    // Run detection
    const predictions = await this.model.predict(tensor);
    const boxes = await predictions[0].array();
    const scores = await predictions[1].array();
    
    // Filter human detections
    const detectedBoxes = [];
    boxes[0].forEach((box, i) => {
      if (scores[0][i] > 0.5) {
        detectedBoxes.push({
          x: Math.round(box[1] * roi.width()),
          y: Math.round(box[0] * roi.height()),
          width: Math.round((box[3] - box[1]) * roi.width()),
          height: Math.round((box[2] - box[0]) * roi.height())
        });
      }
    });

    return detectedBoxes;
  }

  drawDetections(frame, boxes, zone) {
    boxes.forEach(box => {
      frame.rectangle(
        [zone[0][0] + box.x, zone[0][1] + box.y],
        [box.width, box.height],
        [0, 0, 255],
        2
      );
    });
  }
}