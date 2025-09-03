# Anym for Blender

This repo contains a Blender plugin for using the Anym engine.

## Getting Started

### API Key

To use this plugin, you'll need an Anym API key. Go to [app.anym.tech/signup](https://app.anym.tech/signup/) to make an account and obtain your key.

### Installation

1. Download this repository as a zip file (by clicking on the green **Code** button and then at the bottom on **Download ZIP**)
2. In Blender, navigate to **Edit → Preferences → System** and set the **Allow Online Access** variable under the Network tab to true
3. Navigate to **Edit → Preferences → Add-ons**. Open the dropdown menu in the top right corner, click **Install from Disk...**, and select the (still zipped) downloaded folder containing this repository.
4. Finally, click **Install from Disk**.

The plugin is now installed, and an Anym tab will be available in the side bar of the viewport, next to the Item, Tool and View tabs.

## Usage

### Video Tutorial

For a visual guide on using the plugin, check out our [Blender plugin tutorial TODO](https://anym.tech) which demonstrates the total workflow for obtaining a first animation.

### Step-by-Step Workflow

### 0. Obtain your API key
- Make an account on [app.anym.tech/signup](https://app.anym.tech/signup/) and verify your e-mail address
- In the dashboard, click on **Create Company**, fill in a name and click the Confirm button
- Scroll to the bottom of the page and click **Create new API Key**
- Next to the new key, click **Copy Key** to copy your key to your clipboard

#### 1. Setup
- **Enter your API key** in the designated field within the plugin interface

#### 2. Import character
- Select a pose from the **Available Pose:** dropdown menu
  - Creating a rig and using the Anym default character model are both optional and set to true by default
- Click **Import Armature** to set up a posed armature or character and a minimal rig


#### 3. Create keyframes on character
- **Pose your character** by selecting the rig and going into **Pose Mode**
- **Set keyframes** as you normally would (**K** hotkey → **Location & Rotation**)
- Create the key poses as needed for your animation

#### 4. Generate animation
- Click **"Generate Animation"** and the **browser-based previewer** will open automatically
  - On first use, you'll be prompted to enter your login credentials

#### 5. Preview and Iterate
- Review the generated animation in the browser previewer
- If not satisfied, return to Blender and:
  - Adjust your poses, add or modify keyframes
  - Click "Generate Animation" again
- **Repeat this process** until you're happy with the motion

#### 6. Export your animation once final
- In the browser previewer, click **"Unlock Animation"**
- **Name your animation** if desired
- Navigate to the **"Unlocked Animations"** tab
- Click **"Export Animation"**

#### 7. Import into Blender
- Return to the Blender Anym plugin
- Click **"Fetch Animation"**
- Your generated animation will be imported into your Maya scene
- The animation can now be **retargeted and processed** in the same way as you would with mocap data


## Support

For technical support, API access, or general questions, contact **hello@anym.tech**.

## Requirements

- Blender (4.5.1 and up)
- Active internet connection
- Valid Anym API key
