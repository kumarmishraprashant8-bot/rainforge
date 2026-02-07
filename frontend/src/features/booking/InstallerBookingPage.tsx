/**
 * Installer Booking Page
 * Book verified contractors with calendar and quote requests
 */

import { useState } from 'react';
import {
    Calendar, Clock, MapPin, Star, Phone, MessageSquare,
    ChevronLeft, ChevronRight, Check, Shield, Award,
    DollarSign, Wrench, Camera, FileText, Send
} from 'lucide-react';

interface Installer {
    id: string;
    name: string;
    company: string;
    rating: number;
    reviews: number;
    completedJobs: number;
    verified: boolean;
    specializations: string[];
    priceRange: string;
    responseTime: string;
    avatar?: string;
    location: string;
    distance: string;
}

interface TimeSlot {
    time: string;
    available: boolean;
}

const InstallerBookingPage = () => {
    const [selectedInstaller, setSelectedInstaller] = useState<Installer | null>(null);
    const [step, setStep] = useState<'list' | 'profile' | 'booking' | 'confirm'>('list');
    const [selectedDate, setSelectedDate] = useState<Date | null>(null);
    const [selectedTime, setSelectedTime] = useState<string | null>(null);
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [requestDescription, setRequestDescription] = useState('');

    // Demo installers
    const installers: Installer[] = [
        {
            id: 'inst_001',
            name: 'Rajesh Kumar',
            company: 'Jal Mitra Solutions',
            rating: 4.9,
            reviews: 156,
            completedJobs: 234,
            verified: true,
            specializations: ['Residential', 'Commercial', 'Industrial'],
            priceRange: '₹30,000 - ₹80,000',
            responseTime: '< 2 hours',
            location: 'New Delhi',
            distance: '3.2 km'
        },
        {
            id: 'inst_002',
            name: 'Priya Sharma',
            company: 'AquaSave India',
            rating: 4.8,
            reviews: 98,
            completedJobs: 167,
            verified: true,
            specializations: ['Residential', 'Rooftop'],
            priceRange: '₹25,000 - ₹60,000',
            responseTime: '< 4 hours',
            location: 'Gurgaon',
            distance: '8.5 km'
        },
        {
            id: 'inst_003',
            name: 'Amit Patel',
            company: 'GreenDrop Systems',
            rating: 4.7,
            reviews: 72,
            completedJobs: 89,
            verified: true,
            specializations: ['Residential', 'Recharge Wells'],
            priceRange: '₹20,000 - ₹50,000',
            responseTime: '< 6 hours',
            location: 'Noida',
            distance: '12.1 km'
        },
    ];

    // Generate calendar days
    const getDaysInMonth = (date: Date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const days: (Date | null)[] = [];

        // Add empty days for alignment
        for (let i = 0; i < firstDay.getDay(); i++) {
            days.push(null);
        }

        // Add actual days
        for (let i = 1; i <= lastDay.getDate(); i++) {
            days.push(new Date(year, month, i));
        }

        return days;
    };

    const timeSlots: TimeSlot[] = [
        { time: '09:00 AM', available: true },
        { time: '10:00 AM', available: true },
        { time: '11:00 AM', available: false },
        { time: '12:00 PM', available: true },
        { time: '02:00 PM', available: true },
        { time: '03:00 PM', available: true },
        { time: '04:00 PM', available: false },
        { time: '05:00 PM', available: true },
    ];

    const handleBooking = () => {
        // Simulate booking
        setStep('confirm');
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

                {/* Header */}
                <div className="flex items-center gap-4">
                    {step !== 'list' && (
                        <button
                            onClick={() => setStep(step === 'confirm' ? 'booking' : step === 'booking' ? 'profile' : 'list')}
                            className="p-2 bg-white/5 rounded-xl hover:bg-white/10"
                        >
                            <ChevronLeft className="text-white" size={24} />
                        </button>
                    )}
                    <div>
                        <h1 className="text-3xl font-black text-white flex items-center gap-3">
                            <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl">
                                <Wrench className="text-white" size={28} />
                            </div>
                            {step === 'list' && 'Find Installers'}
                            {step === 'profile' && selectedInstaller?.name}
                            {step === 'booking' && 'Book Appointment'}
                            {step === 'confirm' && 'Booking Confirmed'}
                        </h1>
                        <p className="text-gray-400 mt-1">
                            {step === 'list' && 'Verified RWH installation professionals near you'}
                            {step === 'profile' && selectedInstaller?.company}
                            {step === 'booking' && 'Select your preferred date and time'}
                            {step === 'confirm' && 'Your appointment has been scheduled'}
                        </p>
                    </div>
                </div>

                {/* Installer List */}
                {step === 'list' && (
                    <div className="space-y-4">
                        {installers.map(installer => (
                            <div
                                key={installer.id}
                                className="glass rounded-2xl p-6 hover:border-cyan-500/30 border-2 border-transparent transition-all cursor-pointer"
                                onClick={() => { setSelectedInstaller(installer); setStep('profile'); }}
                            >
                                <div className="flex flex-col md:flex-row gap-6">
                                    {/* Avatar */}
                                    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-3xl font-bold flex-shrink-0">
                                        {installer.name.charAt(0)}
                                    </div>

                                    {/* Info */}
                                    <div className="flex-1">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <h3 className="text-xl font-bold text-white">{installer.name}</h3>
                                                    {installer.verified && (
                                                        <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full flex items-center gap-1">
                                                            <Shield size={12} /> Verified
                                                        </span>
                                                    )}
                                                </div>
                                                <p className="text-gray-400">{installer.company}</p>
                                            </div>
                                            <div className="text-right">
                                                <div className="flex items-center gap-1 text-yellow-400">
                                                    <Star size={18} fill="currentColor" />
                                                    <span className="font-bold">{installer.rating}</span>
                                                    <span className="text-gray-500">({installer.reviews})</span>
                                                </div>
                                                <p className="text-gray-500 text-sm flex items-center gap-1 mt-1">
                                                    <MapPin size={14} /> {installer.distance}
                                                </p>
                                            </div>
                                        </div>

                                        <div className="flex flex-wrap gap-2 mt-3">
                                            {installer.specializations.map(spec => (
                                                <span key={spec} className="px-2 py-1 bg-white/5 text-gray-300 text-xs rounded-lg">
                                                    {spec}
                                                </span>
                                            ))}
                                        </div>

                                        <div className="flex flex-wrap gap-6 mt-4 text-sm">
                                            <div className="flex items-center gap-2 text-gray-400">
                                                <Award size={16} className="text-purple-400" />
                                                {installer.completedJobs} jobs completed
                                            </div>
                                            <div className="flex items-center gap-2 text-gray-400">
                                                <Clock size={16} className="text-cyan-400" />
                                                Responds {installer.responseTime}
                                            </div>
                                            <div className="flex items-center gap-2 text-gray-400">
                                                <DollarSign size={16} className="text-green-400" />
                                                {installer.priceRange}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Installer Profile */}
                {step === 'profile' && selectedInstaller && (
                    <div className="grid lg:grid-cols-3 gap-6">
                        {/* Main Profile */}
                        <div className="lg:col-span-2 space-y-6">
                            <div className="glass rounded-2xl p-6">
                                <div className="flex items-center gap-4 mb-6">
                                    <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white text-4xl font-bold">
                                        {selectedInstaller.name.charAt(0)}
                                    </div>
                                    <div>
                                        <h2 className="text-2xl font-bold text-white">{selectedInstaller.name}</h2>
                                        <p className="text-gray-400">{selectedInstaller.company}</p>
                                        <div className="flex items-center gap-2 mt-2">
                                            <div className="flex items-center gap-1 text-yellow-400">
                                                <Star size={16} fill="currentColor" />
                                                <span className="font-bold">{selectedInstaller.rating}</span>
                                            </div>
                                            <span className="text-gray-500">• {selectedInstaller.reviews} reviews</span>
                                            <span className="text-gray-500">• {selectedInstaller.completedJobs} jobs</span>
                                        </div>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-white/5 rounded-xl p-4">
                                        <div className="text-gray-400 text-sm">Response Time</div>
                                        <div className="text-white font-semibold">{selectedInstaller.responseTime}</div>
                                    </div>
                                    <div className="bg-white/5 rounded-xl p-4">
                                        <div className="text-gray-400 text-sm">Price Range</div>
                                        <div className="text-white font-semibold">{selectedInstaller.priceRange}</div>
                                    </div>
                                </div>
                            </div>

                            {/* Reviews Section */}
                            <div className="glass rounded-2xl p-6">
                                <h3 className="text-lg font-bold text-white mb-4">Recent Reviews</h3>
                                {[
                                    { name: 'Amit S.', rating: 5, text: 'Excellent work! Very professional and completed on time.', date: '2 days ago' },
                                    { name: 'Priya M.', rating: 5, text: 'Great installation quality. Highly recommended!', date: '1 week ago' },
                                    { name: 'Rahul K.', rating: 4, text: 'Good work, minor delays but overall satisfied.', date: '2 weeks ago' },
                                ].map((review, idx) => (
                                    <div key={idx} className="py-4 border-b border-white/10 last:border-0">
                                        <div className="flex items-center gap-2 mb-2">
                                            <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center text-white font-bold text-sm">
                                                {review.name.charAt(0)}
                                            </div>
                                            <span className="text-white font-medium">{review.name}</span>
                                            <div className="flex text-yellow-400">
                                                {[...Array(review.rating)].map((_, i) => <Star key={i} size={12} fill="currentColor" />)}
                                            </div>
                                            <span className="text-gray-500 text-sm ml-auto">{review.date}</span>
                                        </div>
                                        <p className="text-gray-400 text-sm">{review.text}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Booking Card */}
                        <div className="glass rounded-2xl p-6 h-fit sticky top-8">
                            <h3 className="text-lg font-bold text-white mb-4">Book This Installer</h3>

                            <div className="space-y-4">
                                <button
                                    onClick={() => setStep('booking')}
                                    className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl hover:scale-[1.02] transition-transform flex items-center justify-center gap-2"
                                >
                                    <Calendar size={20} />
                                    Schedule Site Visit
                                </button>

                                <button className="w-full py-3 bg-white/5 text-white font-medium rounded-xl hover:bg-white/10 transition-colors flex items-center justify-center gap-2">
                                    <MessageSquare size={18} />
                                    Send Message
                                </button>

                                <button className="w-full py-3 bg-white/5 text-white font-medium rounded-xl hover:bg-white/10 transition-colors flex items-center justify-center gap-2">
                                    <FileText size={18} />
                                    Request Quote
                                </button>

                                <div className="pt-4 border-t border-white/10 text-center">
                                    <a href={`tel:+919876543210`} className="text-cyan-400 font-medium flex items-center justify-center gap-2">
                                        <Phone size={16} />
                                        Call Now
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Booking Calendar */}
                {step === 'booking' && selectedInstaller && (
                    <div className="grid lg:grid-cols-2 gap-6">
                        {/* Calendar */}
                        <div className="glass rounded-2xl p-6">
                            <div className="flex items-center justify-between mb-6">
                                <h3 className="text-lg font-bold text-white">Select Date</h3>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1))}
                                        className="p-2 bg-white/5 rounded-lg hover:bg-white/10"
                                    >
                                        <ChevronLeft size={18} className="text-white" />
                                    </button>
                                    <span className="text-white font-medium min-w-[140px] text-center">
                                        {currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                                    </span>
                                    <button
                                        onClick={() => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1))}
                                        className="p-2 bg-white/5 rounded-lg hover:bg-white/10"
                                    >
                                        <ChevronRight size={18} className="text-white" />
                                    </button>
                                </div>
                            </div>

                            <div className="grid grid-cols-7 gap-1 mb-2">
                                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                                    <div key={day} className="text-center text-gray-500 text-sm py-2">{day}</div>
                                ))}
                            </div>

                            <div className="grid grid-cols-7 gap-1">
                                {getDaysInMonth(currentMonth).map((day, idx) => {
                                    const isToday = day && day.toDateString() === new Date().toDateString();
                                    const isSelected = day && selectedDate?.toDateString() === day.toDateString();
                                    const isPast = day && day < new Date(new Date().setHours(0, 0, 0, 0));

                                    return (
                                        <button
                                            key={idx}
                                            disabled={!day || isPast}
                                            onClick={() => day && setSelectedDate(day)}
                                            className={`aspect-square rounded-lg flex items-center justify-center text-sm font-medium transition-all ${!day ? '' :
                                                    isPast ? 'text-gray-600 cursor-not-allowed' :
                                                        isSelected ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' :
                                                            isToday ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500' :
                                                                'text-white hover:bg-white/10'
                                                }`}
                                        >
                                            {day?.getDate()}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>

                        {/* Time Slots */}
                        <div className="glass rounded-2xl p-6">
                            <h3 className="text-lg font-bold text-white mb-6">Select Time</h3>

                            {selectedDate ? (
                                <>
                                    <p className="text-gray-400 mb-4">
                                        Available slots for {selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
                                    </p>
                                    <div className="grid grid-cols-2 gap-3 mb-6">
                                        {timeSlots.map(slot => (
                                            <button
                                                key={slot.time}
                                                disabled={!slot.available}
                                                onClick={() => setSelectedTime(slot.time)}
                                                className={`py-3 rounded-xl font-medium transition-all ${!slot.available ? 'bg-white/5 text-gray-600 cursor-not-allowed line-through' :
                                                        selectedTime === slot.time ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white' :
                                                            'bg-white/5 text-white hover:bg-white/10'
                                                    }`}
                                            >
                                                {slot.time}
                                            </button>
                                        ))}
                                    </div>

                                    <div className="space-y-4">
                                        <textarea
                                            value={requestDescription}
                                            onChange={(e) => setRequestDescription(e.target.value)}
                                            placeholder="Describe your requirements (optional)..."
                                            className="w-full p-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 resize-none h-24 focus:outline-none focus:border-cyan-500"
                                        />

                                        <button
                                            onClick={handleBooking}
                                            disabled={!selectedTime}
                                            className="w-full py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl hover:scale-[1.02] transition-transform disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                                        >
                                            <Send size={20} />
                                            Confirm Booking
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <p className="text-gray-500 text-center py-12">Please select a date first</p>
                            )}
                        </div>
                    </div>
                )}

                {/* Confirmation */}
                {step === 'confirm' && selectedInstaller && selectedDate && selectedTime && (
                    <div className="glass rounded-2xl p-8 text-center max-w-lg mx-auto">
                        <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-green-500/20 flex items-center justify-center">
                            <Check className="text-green-400" size={40} />
                        </div>
                        <h2 className="text-2xl font-bold text-white mb-2">Booking Confirmed!</h2>
                        <p className="text-gray-400 mb-6">Your site visit has been scheduled</p>

                        <div className="bg-white/5 rounded-xl p-4 mb-6 text-left space-y-3">
                            <div className="flex items-center gap-3">
                                <Wrench className="text-purple-400" size={18} />
                                <span className="text-white">{selectedInstaller.name} - {selectedInstaller.company}</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <Calendar className="text-cyan-400" size={18} />
                                <span className="text-white">{selectedDate.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' })}</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <Clock className="text-yellow-400" size={18} />
                                <span className="text-white">{selectedTime}</span>
                            </div>
                        </div>

                        <p className="text-gray-500 text-sm mb-6">
                            You will receive a confirmation SMS and email shortly. The installer will contact you before the visit.
                        </p>

                        <div className="flex gap-3">
                            <button
                                onClick={() => { setStep('list'); setSelectedInstaller(null); setSelectedDate(null); setSelectedTime(null); }}
                                className="flex-1 py-3 bg-white/5 text-white rounded-xl hover:bg-white/10"
                            >
                                Back to Installers
                            </button>
                            <a href="/" className="flex-1 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-xl font-semibold text-center">
                                Go Home
                            </a>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default InstallerBookingPage;
