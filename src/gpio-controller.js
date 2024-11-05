import { Gpio } from 'onoff';

export class RelayController {
  constructor(pin1, pin2, duration) {
    this.relay1 = new Gpio(pin1, 'out');
    this.relay2 = new Gpio(pin2, 'out');
    this.duration = duration;
  }

  async controlRelay(relay) {
    await relay.write(1);
    await new Promise(resolve => setTimeout(resolve, this.duration * 1000));
    await relay.write(0);
  }

  activateRelay(cameraIndex) {
    const relay = cameraIndex === 0 ? this.relay1 : this.relay2;
    this.controlRelay(relay).catch(console.error);
  }

  cleanup() {
    this.relay1.unexport();
    this.relay2.unexport();
  }
}