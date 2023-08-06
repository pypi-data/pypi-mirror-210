import torchvision
import torchvision.transforms as transforms
import matplotlib.pyplot as plt
from torch.utils.data import DataLoader
from greenlab.conv2d_pca import Conv2d_PCA


def test_conv2d_pca():
    # Define transformations to apply to the data
    transform = transforms.Compose(
        [
            transforms.ToTensor(),
        ]
    )

    # Load the CIFAR-10 dataset
    trainset = torchvision.datasets.CIFAR10(
        root="./data", train=True, download=True, transform=transform
    )
    testset = torchvision.datasets.CIFAR10(
        root="./data", train=False, download=True, transform=transform
    )

    # Create data loaders
    trainloader = DataLoader(trainset, batch_size=100, shuffle=True, num_workers=2)
    testloader = DataLoader(testset, batch_size=100, shuffle=False, num_workers=2)

    images, labels = next(iter(trainloader))
    print("Image Shape", images.shape)
    print("Label Shape", labels.shape)

    conv = Conv2d_PCA(3, 15, kernel_size=3, stride=1, padding=1, mode="pca")
    output = conv(images)
    print(conv.explained_variance_ratio_)
    print("Output Shape", output.shape)
    plt.imshow(images[0].permute(1, 2, 0).detach().numpy())
    plt.show()

    plt.figure(figsize=(20, 5))
    for i in range(15):
        plt.subplot(3, 9, i + 1)
        plt.imshow(output[0, i].detach().numpy(), cmap="gray")
        plt.tight_layout()
        plt.title(f"{conv.explained_variance_ratio_[i]:.2f}")
        plt.axis("off")
    plt.show()


# if __name__ == "__main__":
#     test_conv2d_pca()
