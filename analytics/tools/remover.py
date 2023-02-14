
class NoisyObjectRemover:
    def __init__(self, detector):
        self.detector = detector

    def is_removable(self, capture):
        while True:
            frame = capture.read()
            if frame is None:
                break

            # detect objects from frame
            boxes, _, _, _ = self.detector.detect(frame)

            return False if boxes else True

