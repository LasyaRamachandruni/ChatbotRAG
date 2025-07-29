# 🤖 MLK Library AI Chatbot

A cheerful, quirky AI chatbot designed specifically for the Dr. Martin Luther King Jr. Library, built with free tools and ready to embed into Google Sites!

## ✨ Features

- 🎨 **Beautiful Modern UI** - Clean, responsive design with smooth animations
- 🌟 **Cheerful Personality** - Quirky, friendly responses that delight users
- 🏛️ **MLK Library Themed** - Features the iconic MLK Library building as avatar
- 📚 **Comprehensive Knowledge** - Knows about library services, hours, events, and more
- 🔧 **Easy to Embed** - Simple integration with Google Sites
- 📱 **Mobile Responsive** - Works perfectly on all devices
- 🆓 **100% Free** - No API costs or external dependencies
- ⚡ **Lightning Fast** - Instant responses with no delays

## 🚀 Quick Start

### Option 1: Direct Embed (Recommended)
1. Copy the embed code from `embed.html`
2. Paste it into your Google Sites HTML embed block
3. Publish your site - that's it! 🎉

### Option 2: Host Yourself
1. Upload `index.html`, `style.css`, and `script.js` to your web server
2. Use iframe embed code to include it in Google Sites

## 📋 Files Structure

```
├── index.html          # Main chatbot interface
├── style.css           # Beautiful styling and animations
├── script.js           # Chatbot logic and responses
├── embed.html          # Embedding guide and code
├── README.md           # This file
└── requirements.txt    # Python dependencies (if needed)
```

## 🎯 What the Chatbot Knows

The chatbot is equipped with comprehensive knowledge about:

- 🕐 **Library Hours** - Opening and closing times
- 📍 **Location & Directions** - Address, parking, transit info
- 📚 **Services** - All library services and resources
- 🎉 **Events & Programs** - Information about library activities
- 👥 **Study Spaces** - Meeting rooms and study areas
- 💻 **Technology** - Computers, Wi-Fi, printing services
- 🎨 **Special Collections** - MLK Collection, art installations
- 👶 **Family Services** - Children's programs and teen spaces
- 💼 **Career Services** - SJPL Works and business resources

## 🛠️ Customization

### Change Colors
Edit the CSS gradient values:
```css
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Update Avatar
Replace the image URL in the HTML:
```html
<img src="YOUR_IMAGE_URL" alt="Your Library">
```

### Add More Responses
Extend the `generateResponse()` function in `script.js`:
```javascript
if (this.containsWords(lowerMessage, ['your', 'keywords'])) {
    return 'Your custom response here! 😊';
}
```

## 🌐 Embedding in Google Sites

### Step-by-Step Guide:

1. **Open Google Sites Editor**
   - Go to your Google Sites page
   - Click "Edit" to enter edit mode

2. **Insert Embed Block**
   - Click "Insert" in the toolbar
   - Select "Embed"
   - Choose "Embed code"

3. **Paste the Code**
   - Copy the complete embed code from `embed.html`
   - Paste it into the embed dialog
   - Click "Add"

4. **Publish**
   - Click "Publish" to make your chatbot live!

## 💡 Pro Tips

- **Test Responsiveness**: Check how it looks on mobile devices
- **Monitor Performance**: The chatbot is lightweight and won't slow down your site
- **Update Content**: Easily modify responses to match your specific needs
- **Accessibility**: Built with screen readers and keyboard navigation in mind

## 🔧 Technical Details

- **No External APIs**: Works completely offline
- **Vanilla JavaScript**: No frameworks required
- **CSS3 Animations**: Smooth, modern interactions
- **Mobile-First Design**: Optimized for all screen sizes
- **Cross-Browser Compatible**: Works in all modern browsers

## 🎨 Design Philosophy

The chatbot follows these design principles:
- **Friendly & Approachable**: Warm colors and cheerful language
- **Professional Yet Playful**: Maintains library credibility while being fun
- **Accessible**: High contrast, clear fonts, keyboard navigation
- **Fast & Lightweight**: Minimal resource usage

## 📞 Support

If you need help customizing or deploying the chatbot:
1. Check the `embed.html` file for detailed instructions
2. Review the code comments for customization guidance
3. Test thoroughly before going live

## 🎉 Success Stories

This chatbot is designed to:
- ✅ Reduce repetitive questions to library staff
- ✅ Provide 24/7 assistance to website visitors
- ✅ Enhance user experience with instant responses
- ✅ Showcase the library's modern, tech-forward approach

## 🔮 Future Enhancements

Potential improvements you could add:
- Integration with library catalog search
- Real-time event calendar integration
- Multi-language support
- Voice interaction capabilities
- Analytics and usage tracking

---

**Built with ❤️ for the MLK Library Community**

*Ready to delight your visitors with an amazing chatbot experience!* ✨