import os

import paddle as pd

from misc.imutils import save_image
from models.networks import *


class CDEvaluator():

    def __init__(self, args):

        self.n_class = args.n_class
        # define G
        self.net_G = define_G(args=args, gpu_ids=args.gpu_ids)

        self.device = pd.get_device()

        print(self.device)

        self.checkpoint_dir = args.checkpoint_dir

        self.pred_dir = args.output_folder
        os.makedirs(self.pred_dir, exist_ok=True)

    def load_checkpoint(self, checkpoint_name='best_ckpt.pdparams'):

        if os.path.exists(os.path.join(self.checkpoint_dir, checkpoint_name)):
            # load the entire checkpoint
            checkpoint = pd.load(
                os.path.join(
                    self.checkpoint_dir,
                    checkpoint_name))

            self.net_G.set_state_dict(checkpoint['model_G_state_dict'])
            self.net_G.to(self.device)
            # update some other states
            self.best_val_acc = checkpoint['best_val_acc']
            self.best_epoch_id = checkpoint['best_epoch_id']

            print("best_acc: ", self.best_val_acc)

        else:
            raise FileNotFoundError('no such checkpoint %s' % checkpoint_name)
        return self.net_G

    def _visualize_pred(self):
        pred = pd.argmax(self.G_pred, axis=1, keepdim=True)
        pred_vis = pred * 255
        return pred_vis

    def _forward_pass(self, batch):
        self.batch = batch
        img_in1 = batch['A']
        img_in2 = batch['B']
        self.shape_h = img_in1.shape[-2]
        self.shape_w = img_in1.shape[-1]

        self.G_pred = self.net_G(img_in1, img_in2)[-1]
        return self._visualize_pred()

    def eval(self):
        self.net_G.eval()

    def _save_predictions(self):
        """
        保存模型输出结果，二分类图像
        """

        preds = self._visualize_pred()
        name = self.batch['name']
        for i, pred in enumerate(preds):
            file_name = os.path.join(
                self.pred_dir, name[i].replace('.jpg', '.png'))
            pred = pred[0].cpu().numpy()
            save_image(pred, file_name)
