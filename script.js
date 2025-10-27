class MLKLibraryChatbot {
    constructor() {
        this.isOpen = false;
        this.isTyping = false;
        this.websiteContent = null;
        this.knowledgeBase = null;
        this.init();
        this.loadWebsiteContent();
        this.loadKnowledgeBase();
    }

    init() {
        this.bindEvents();
        this.setupQuickActions();
    }

    bindEvents() {
        const chatButton = document.getElementById('chatbot-button');
        const closeBtn = document.getElementById('close-chat');
        const sendBtn = document.getElementById('send-btn');
        const userInput = document.getElementById('user-input');

        chatButton.addEventListener('click', () => this.toggleChat());
        closeBtn.addEventListener('click', () => this.closeChat());
        sendBtn.addEventListener('click', () => this.sendMessage());
        
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize input
        userInput.addEventListener('input', (e) => {
            this.adjustInputHeight(e.target);
        });
    }

    setupQuickActions() {
        const quickBtns = document.querySelectorAll('.quick-btn');
        quickBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.getAttribute('data-message');
                this.sendQuickMessage(message);
            });
        });
    }

    toggleChat() {
        const container = document.getElementById('chatbot-container');
        
        if (this.isOpen) {
            this.closeChat();
        } else {
            container.classList.remove('hidden');
            setTimeout(() => {
                container.classList.add('visible');
            }, 10);
            this.isOpen = true;
        }
    }

    closeChat() {
        const container = document.getElementById('chatbot-container');
        container.classList.remove('visible');
        setTimeout(() => {
            container.classList.add('hidden');
        }, 400);
        this.isOpen = false;
    }

    async sendMessage() {
        const input = document.getElementById('user-input');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;

        input.value = '';
        this.addMessage(message, 'user');
        this.showTyping();

        try {
            const response = await this.generateResponse(message);
            this.hideTyping();
            this.addMessage(response, 'bot');
        } catch (error) {
            this.hideTyping();
            this.addMessage("Oops! 😅 I'm having a tiny technical hiccup right now. But don't worry - I'm still here to help! Could you try asking me again in a moment? 🌟", 'bot');
        }
    }

    sendQuickMessage(message) {
        document.getElementById('user-input').value = message;
        this.sendMessage();
    }

    addMessage(text, type) {
        const messagesContainer = document.getElementById('messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}-message`;

        if (type === 'user') {
            messageDiv.innerHTML = `
                <div class="message-avatar">U</div>
                <div class="message-content">
                    <p>${this.escapeHtml(text)}</p>
                </div>
            `;
        } else {
            messageDiv.innerHTML = `
                <div class="message-avatar">
                    <img src="https://www.sjpl.org/sites/default/files/styles/hero_image/public/2023-09/king-library-entrance-dusk.jpg" alt="MLK Library">
                </div>
                <div class="message-content">
                    <p>${text}</p>
                </div>
            `;
        }

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTyping() {
        this.isTyping = true;
        document.getElementById('typing').classList.remove('hidden');
        document.getElementById('send-btn').disabled = true;
    }

    hideTyping() {
        this.isTyping = false;
        document.getElementById('typing').classList.add('hidden');
        document.getElementById('send-btn').disabled = false;
    }

    async loadWebsiteContent() {
        // Since we can't directly scrape the Google Sites content due to CORS,
        // we'll create a knowledge base with the information we gathered
        this.websiteContent = {
            libraryInfo: {
                name: "Dr. Martin Luther King Jr. Library",
                location: "150 E San Fernando St, San Jose, CA 95112",
                phone: "(408) 808-2000",
                description: "A unique partnership between San José Public Library and San José State University, serving as both the city's main library and the university library.",
                hours: {
                    "Monday-Thursday": "8:00 AM - 8:00 PM",
                    "Friday-Saturday": "8:00 AM - 6:00 PM",
                    "Sunday": "1:00 PM - 6:00 PM"
                }
            },
            services: [
                "Digital Humanities Center",
                "SJPL Works: Career & Business services",
                "Teen HQ: Teen Center",
                "Wee Explore PlaySpace",
                "Study and meeting rooms",
                "Computer and printing services",
                "Free Wi-Fi",
                "Special collections",
                "California Room - Local History",
                "Social work services",
                "Maker spaces"
            ],
            specialCollections: [
                "Dr. Martin Luther King Jr. Collection - books, videos, and audio recordings about Dr. King and the Civil Rights movement",
                "California Room - local and state history materials",
                "SJSU Library Special Collections including Beethoven Center and Steinbeck Center"
            ],
            features: [
                "Nine floors of resources",
                "Public art installations by Mel Chin",
                "Bronze bust of Dr. Martin Luther King Jr.",
                "Flexible workspaces",
                "Technology-equipped meeting rooms",
                "Exhibit areas",
                "Café on-site"
            ]
        };
    }

    async loadKnowledgeBase() {
        try {
            // Load knowledge base files
            const orgChartResponse = await fetch('knowledge_base/org_chart_sjsu_king_library.md');
            const contactsResponse = await fetch('knowledge_base/contacts_help_services.md');
            const parkingResponse = await fetch('knowledge_base/sjsu_parking_permit_request.md');
            const eventFundingResponse = await fetch('knowledge_base/event_funding_request.md');
            
            const orgChartText = await orgChartResponse.text();
            const contactsText = await contactsResponse.text();
            const parkingText = await parkingResponse.text();
            const eventFundingText = await eventFundingResponse.text();
            
            this.knowledgeBase = {
                orgChart: orgChartText,
                contacts: contactsText,
                parking: parkingText,
                eventFunding: eventFundingText
            };
        } catch (error) {
            console.log('Could not load knowledge base files:', error);
            this.knowledgeBase = null;
        }
    }

    searchKnowledgeBase(query) {
        if (!this.knowledgeBase) return null;
        
        const lowerQuery = query.toLowerCase();
        const results = [];
        
        // Handle name variations (e.g., "Michel Meth" vs "Michael Meth")
        const nameVariations = {
            'michel meth': ['michael meth'],
            'lisa josefi': ['lisa josefik'],
            'lisa josefik': ['lisa josefi']
        };
        
        let searchTerms = [lowerQuery];
        if (nameVariations[lowerQuery]) {
            searchTerms = searchTerms.concat(nameVariations[lowerQuery]);
        }
        
        // Search in all knowledge base files
        const files = [
            { name: 'orgChart', content: this.knowledgeBase.orgChart },
            { name: 'contacts', content: this.knowledgeBase.contacts },
            { name: 'parking', content: this.knowledgeBase.parking },
            { name: 'eventFunding', content: this.knowledgeBase.eventFunding }
        ];
        
        for (const file of files) {
            const lines = file.content.split('\n');
            for (const line of lines) {
                const lowerLine = line.toLowerCase();
                for (const term of searchTerms) {
                    if (lowerLine.includes(term)) {
                        results.push(line.trim());
                        break; // Avoid duplicate lines
                    }
                }
            }
        }
        
        return results.length > 0 ? results : null;
    }

    async generateResponse(userMessage) {
        const lowerMessage = userMessage.toLowerCase();
        
        // First, try to search the knowledge base for people or specific information
        const knowledgeResults = this.searchKnowledgeBase(userMessage);
        if (knowledgeResults) {
            let response = "I found some information for you! 📚\n\n";
            
            // Format the results nicely
            const formattedResults = knowledgeResults.map(result => {
                // Remove markdown formatting for cleaner display
                return result.replace(/^[-*]\s*/, '').replace(/\*\*(.*?)\*\*/g, '$1');
            });
            
            response += formattedResults.join('\n');
            response += "\n\nIs there anything specific about this information you'd like to know more about? 😊";
            return response;
        }
        
        // Enhanced pattern matching with cheerful responses
        if (this.containsWords(lowerMessage, ['hello', 'hi', 'hey', 'greetings'])) {
            return this.getRandomResponse([
                "Hello there! 👋 Welcome to the MLK Library! I'm absolutely delighted to meet you! How can I brighten your day with some amazing library info? ✨",
                "Hey! 🌟 What a wonderful day to explore everything our fantastic library has to offer! What brings you here today?",
                "Hi there, superstar! 🎉 I'm your cheerful library assistant, and I'm here to make your library experience absolutely amazing! What can I help you discover?"
            ]);
        }

        if (this.containsWords(lowerMessage, ['hours', 'open', 'close', 'time'])) {
            return `🕐 Our fantastic hours are:\n\n📅 **Monday-Thursday:** 8:00 AM - 8:00 PM\n📅 **Friday-Saturday:** 8:00 AM - 6:00 PM\n📅 **Sunday:** 1:00 PM - 6:00 PM\n\nWe're open almost every day to serve you! Come visit us anytime! 🌟`;
        }

        if (this.containsWords(lowerMessage, ['card', 'library card', 'membership', 'sign up'])) {
            return `📚 Getting a library card is super easy and totally FREE! 🎉\n\nYou can get one if you:\n✅ Live in San José\n✅ Work in San José\n✅ Learn in San José\n\nJust visit us at the library with a valid ID, and we'll get you set up in no time! You'll have access to books, eBooks, computers, events, and SO much more! It's like having a key to endless knowledge! 🗝️✨`;
        }

        if (this.containsWords(lowerMessage, ['location', 'address', 'where', 'directions'])) {
            return `📍 You can find us at:\n\n**150 E San Fernando St**\n**San Jose, CA 95112**\n\n🚗 **Parking:** FREE for the first 90 minutes at the 4th St. Garage!\n🚌 **Transit:** We're accessible by multiple bus routes and light rail\n\nWe're right in the heart of downtown San José - can't miss us! The building is absolutely beautiful! 🏛️✨`;
        }

        if (this.containsWords(lowerMessage, ['services', 'what do you offer', 'resources', 'facilities'])) {
            const services = this.websiteContent.services.slice(0, 8);
            return `🎯 We offer SO many amazing services! Here are some highlights:\n\n${services.map(service => `🌟 ${service}`).join('\n')}\n\nAnd that's just the beginning! We also have special collections, public art, a café, and 9 floors of incredible resources! What specific service interests you most? 😊`;
        }

        if (this.containsWords(lowerMessage, ['events', 'programs', 'activities', 'workshops'])) {
            return `🎉 We host TONS of exciting events and programs! Here's what you can expect:\n\n🎨 **Creative workshops** - Art, maker spaces, and hands-on learning\n📚 **Educational programs** - For all ages from toddlers to seniors\n💻 **Tech training** - Digital skills and computer classes\n🎭 **Cultural events** - Celebrating our diverse community\n👥 **Community gatherings** - Meet new people and make connections!\n\nEvents happen throughout the week! Check our website or visit us to see what's coming up. There's always something fun happening here! ✨`;
        }

        if (this.containsWords(lowerMessage, ['study', 'study rooms', 'meeting rooms', 'space'])) {
            return `📖 We have AMAZING spaces for studying and meetings! \n\n🏠 **Study Rooms:** Perfect for focused individual or group study\n👥 **Meeting Rooms:** Great for team projects and presentations\n💻 **Tech-equipped spaces:** With all the tools you need\n🤫 **Quiet zones:** For deep concentration\n☕ **Collaborative areas:** Where ideas flow freely!\n\nYou can reserve rooms in advance, and we have spaces for every type of learner! Whether you're cramming for exams or brainstorming the next big idea, we've got you covered! 🌟`;
        }

        if (this.containsWords(lowerMessage, ['parking', 'car', 'drive'])) {
            return `🚗 Great news about parking! \n\n🎉 **FREE parking** for the first 90 minutes at the 4th Street Garage!\n📍 The garage is super convenient and close to our main entrance\n⏰ Perfect for quick visits, studying sessions, or browsing our collections\n\nAfter 90 minutes, regular parking rates apply, but honestly, once you discover everything we have here, you might want to stay all day! 😄✨`;
        }

        if (this.containsWords(lowerMessage, ['mlk', 'martin luther king', 'king collection', 'civil rights'])) {
            return `👑 The Dr. Martin Luther King Jr. Collection is one of our most treasured resources! \n\n📚 **What's included:**\n🎬 Books, videos, and audio recordings about Dr. King\n📰 Special gallery with photos and newspaper clippings\n📅 Timeline of Dr. King's incredible life\n🏛️ Bronze bust by renowned artist Sascha Schnittmann\n\n✨ It's located on our Third Floor and everything can be checked out! This collection beautifully honors Dr. King's legacy and the Civil Rights movement. It's truly inspiring! 🌟`;
        }

        if (this.containsWords(lowerMessage, ['teen', 'teenager', 'youth', 'teen hq'])) {
            return `🎮 TeenHQ is absolutely AMAZING! It's our dedicated teen center where creativity and innovation flourish! \n\n🌟 **What makes it special:**\n💻 Latest technology and maker tools\n🎨 Creative spaces for projects\n👥 Community of awesome teens\n🎯 Programs designed just for you\n🚀 Space to be yourself and explore your interests!\n\nIt's like a teen dream hub where you can hang out, learn, create, and connect with other incredible young people! Come check it out! 🎉`;
        }

        if (this.containsWords(lowerMessage, ['children', 'kids', 'family', 'playspace'])) {
            return `👶 The Wee Explore PlaySpace is pure magic for little ones! \n\n🎈 **Perfect for:**\n🧸 Children to learn through play\n👨‍👩‍👧‍👦 Family bonding time\n🎯 Open-ended exploration\n🌱 Growing young minds\n\n📍 Located right in our Children's Room, it's designed to spark curiosity and joy! We also have storytimes, take-home materials, and programs for the whole family. Kids absolutely LOVE it here! 🌈✨`;
        }

        if (this.containsWords(lowerMessage, ['computer', 'internet', 'wifi', 'printing'])) {
            return `💻 We're totally tech-friendly! Here's what we offer:\n\n📶 **FREE Wi-Fi** throughout the entire building\n🖥️ **Public computers** for research, work, and fun\n🖨️ **Printing services** for all your document needs\n📱 **Device charging stations**\n💻 **Laptop lending** - you can actually borrow Chromebooks, iPads, and laptops!\n\nWhether you need to finish homework, apply for jobs, or just browse the web, we've got all the tech support you need! 🚀`;
        }

        if (this.containsWords(lowerMessage, ['art', 'mel chin', 'public art', 'sculptures'])) {
            return `🎨 Our public art is absolutely breathtaking! \n\n🦋 **"Recolecciones" by Mel Chin** - Stunning installations on each floor\n🗽 **Bronze bust of Dr. Martin Luther King Jr.** - A powerful tribute in our lobby\n🎭 **Rotating exhibits** throughout the building\n\nThe art here tells stories, inspires thoughts, and creates this amazing atmosphere of creativity and learning! Every floor has something beautiful to discover. It's like walking through a gallery while you explore knowledge! ✨🖼️`;
        }

        if (this.containsWords(lowerMessage, ['career', 'job', 'business', 'sjpl works'])) {
            return `💼 SJPL Works is your career and business superpower! \n\n🚀 **We help with:**\n📝 Resume building and job applications\n💡 Small business development\n👔 Interview preparation\n💻 Digital skills training\n🌐 Networking opportunities\n📊 Entrepreneurship resources\n\nWhether you're starting your career, changing paths, or launching a business, we have the tools and support to help you succeed! Your dreams are our mission! 🌟💪`;
        }

        if (this.containsWords(lowerMessage, ['contact', 'phone', 'call', 'reach'])) {
            return `📞 We'd love to hear from you! Here's how to reach us:\n\n☎️ **Phone:** (408) 808-2000\n📍 **Visit us:** 150 E San Fernando St, San Jose, CA 95112\n💬 **In person:** We're here and ready to help!\n\nOur amazing staff is always happy to assist you with anything you need. Don't hesitate to reach out - we're here to make your library experience incredible! 🌟😊`;
        }

        if (this.containsWords(lowerMessage, ['thank', 'thanks', 'appreciate'])) {
            return this.getRandomResponse([
                "Aww, you're so welcome! 🥰 It absolutely makes my day to help wonderful people like you! Come back anytime - we'll be here with smiles and knowledge! ✨",
                "You're incredibly kind! 😊 Thank YOU for being part of our amazing library community! We're lucky to have you! 🌟",
                "It's my absolute pleasure! 🎉 Helping awesome library users like you is what makes this job so rewarding! See you soon! 💫"
            ]);
        }

        if (this.containsWords(lowerMessage, ['bye', 'goodbye', 'see you', 'later'])) {
            return this.getRandomResponse([
                "Goodbye for now! 👋 Thanks for chatting with me - you've made my day brighter! Come back soon, and remember, we're always here when you need us! ✨📚",
                "See you later, superstar! 🌟 It was wonderful helping you today! Don't be a stranger - our doors (and my chat window) are always open! 😊",
                "Bye bye! 🎉 Keep being awesome, and remember - the MLK Library is your home for learning, growing, and discovering amazing things! Until next time! 💫"
            ]);
        }

        // Default response with helpful suggestions
        return `That's a great question! 🤔 While I might not have the exact answer you're looking for, I'm here to help with anything about our amazing library! \n\n💡 **I can tell you about:**\n📍 Hours and location\n📚 Services and resources\n🎉 Events and programs\n🏛️ Special collections\n💻 Technology and study spaces\n\nWhat would you like to know more about? I'm excited to help you discover all the wonderful things our library has to offer! ✨😊`;
    }

    containsWords(text, words) {
        return words.some(word => text.includes(word));
    }

    getRandomResponse(responses) {
        return responses[Math.floor(Math.random() * responses.length)];
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    adjustInputHeight(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new MLKLibraryChatbot();
});

// Export for embedding in other sites
window.MLKLibraryChatbot = MLKLibraryChatbot;