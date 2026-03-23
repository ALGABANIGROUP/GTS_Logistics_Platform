import React, { useState } from 'react';
import {
    Container,
    Paper,
    Typography,
    Box,
    Stepper,
    Step,
    StepLabel,
    Button,
    Grid,
    TextField,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    Alert,
    Card,
    CardContent,
    IconButton,
    InputAdornment
} from '@mui/material';
import {
    Person as PersonIcon,
    Business as BusinessIcon,
    LocalShipping as ShippingIcon,
    Link as LinkIcon,
    Visibility,
    VisibilityOff,
    ArrowForward,
    CheckCircle
} from '@mui/icons-material';
import PortalBackground from "../../components/layout/PortalBackground";

const TMSRegister = () => {
    const [activeStep, setActiveStep] = useState(0);
    const [userType, setUserType] = useState('');
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        confirmPassword: '',
        phone: '',
        country: 'SA',
        companyName: '',
        industry: '',
        shippingVolume: '',
        carrierName: '',
        fleetSize: '',
        serviceAreas: '',
        licenseNumber: '',
        brokerageName: '',
        yearsExperience: '',
        termsAccepted: false,
        privacyAccepted: false
    });
    const [errors, setErrors] = useState({});
    const [showPassword, setShowPassword] = useState(false);
    const [submitting, setSubmitting] = useState(false);
    const [success, setSuccess] = useState(false);

    const steps = [
        'Select user type',
        'Basic information',
        'Specialized information',
        'Review and confirm'
    ];

    const userTypes = [
        {
            value: 'shipper',
            label: 'Shipper',
            description: 'I want to ship my goods via a reliable platform',
            icon: <BusinessIcon />, color: '#1976d2'
        },
        {
            value: 'carrier',
            label: 'Carrier',
            description: 'I am a transportation company that wants to join the network',
            icon: <ShippingIcon />, color: '#2e7d32'
        },
        {
            value: 'broker',
            label: 'Broker',
            description: 'Connect shippers and carriers',
            icon: <LinkIcon />, color: '#9c27b0'
        }
    ];

    const handleUserTypeSelect = (type) => {
        setUserType(type);
        setFormData(prev => ({ ...prev, userType: type }));
        handleNext();
    };
    const handleNext = () => setActiveStep((prev) => prev + 1);
    const handleBack = () => setActiveStep((prev) => prev - 1);
    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
    };
    const buildRegistrationPayload = () => {
        const companyName = formData.companyName || formData.carrierName || formData.brokerageName || '';
        const contactName = companyName || formData.email;
        const industryTypeMap = {
            shipper: '3pl',
            carrier: 'carrier',
            broker: 'freight_broker'
        };
        const planMap = {
            low: 'starter',
            medium: 'professional',
            high: 'enterprise',
            'very-high': 'enterprise'
        };
        const primaryArea = formData.serviceAreas
            ? formData.serviceAreas.split(',')[0].trim()
            : '';
        const notes = [
            userType ? `User type: ${userType}` : '',
            formData.country ? `Country: ${formData.country}` : '',
            formData.shippingVolume ? `Monthly volume: ${formData.shippingVolume}` : '',
            formData.licenseNumber ? `License number: ${formData.licenseNumber}` : '',
            formData.fleetSize ? `Fleet size: ${formData.fleetSize}` : '',
            formData.serviceAreas ? `Service areas: ${formData.serviceAreas}` : '',
            formData.yearsExperience ? `Years of experience: ${formData.yearsExperience}` : ''
        ].filter(Boolean).join(' | ');

        return {
            company_name: companyName || 'Unspecified company',
            contact_name: contactName || 'Unspecified contact',
            contact_email: formData.email,
            contact_phone: formData.phone || null,
            company_website: null,
            industry_type: industryTypeMap[userType] || 'freight_broker',
            state_province: null,
            city: primaryArea || null,
            requested_plan: planMap[formData.shippingVolume] || 'starter',
            notes: notes || null
        };
    };
    const validateStep = () => {
        const newErrors = {};
        if (activeStep === 1) {
            if (!formData.email) newErrors.email = 'Email required';
            else if (!/\S+@\S+\.\S+/.test(formData.email)) newErrors.email = 'Invalid email';
            if (!formData.password) newErrors.password = 'Password required';
            else if (formData.password.length < 6) newErrors.password = 'Password must be at least 6 characters';
            if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
            if (!formData.phone) newErrors.phone = 'Phone number required';
        }
        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };
    const handleSubmit = async () => {
        if (!validateStep()) return;
        setSubmitting(true);
        try {
            const payload = buildRegistrationPayload();
            const response = await fetch('/api/v1/admin/tms-requests/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                setSuccess(true);
            } else {
                const result = await response.json().catch(() => ({}));
                throw new Error(result?.detail || result?.message || 'Failed to register');
            }
        } catch (error) {
            setErrors({ submit: error.message });
        } finally {
            setSubmitting(false);
        }
    };
    const renderStepContent = () => {
        switch (activeStep) {
            case 0:
                return (
                    <Box sx={{ mt: 4 }}>
                        <Typography variant="h5" align="center" gutterBottom>Choose your account type</Typography>
                        <Typography color="text.secondary" align="center" paragraph>Choose the appropriate role to activate the features that are right for you.</Typography>
                        <Grid container spacing={3} sx={{ mt: 2 }}>
                            {userTypes.map((type) => (
                                <Grid item xs={12} md={4} key={type.value}>
                                    <Card
                                        sx={{ cursor: 'pointer', border: userType === type.value ? `2px solid ${type.color}` : '1px solid #e0e0e0', transition: 'all 0.3s', height: '100%', '&:hover': { transform: 'translateY(-4px)', boxShadow: 6, borderColor: type.color } }}
                                        onClick={() => handleUserTypeSelect(type.value)}
                                    >
                                        <CardContent sx={{ textAlign: 'center', py: 4 }}>
                                            <Box sx={{ backgroundColor: `${type.color}20`, width: 80, height: 80, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto', mb: 2 }}>
                                                {React.cloneElement(type.icon, { sx: { fontSize: 40, color: type.color } })}
                                            </Box>
                                            <Typography variant="h6" sx={{ fontWeight: 'bold', mb: 1 }}>{type.label}</Typography>
                                            <Typography variant="body2" color="text.secondary" paragraph>{type.description}</Typography>
                                            <Button variant="outlined" endIcon={<ArrowForward />} sx={{ borderColor: type.color, color: type.color }}>Select this type</Button>
                                        </CardContent>
                                    </Card>
                                </Grid>
                            ))}
                        </Grid>
                        <Alert severity="info" sx={{ mt: 4 }}>
                            <Typography variant="body2"><strong>Note:</strong> All requests are subject to review and approval by the platform administration. You will receive an email when your account is activated.</Typography>
                        </Alert>
                    </Box>
                );
            case 1:
                return (
                    <Box sx={{ mt: 4 }}>
                        <Typography variant="h5" gutterBottom>Basic information</Typography>
                        <Grid container spacing={3}>
                            <Grid item xs={12}>
                                <TextField fullWidth label="Email" name="email" value={formData.email} onChange={handleInputChange} error={!!errors.email} helperText={errors.email} required />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField fullWidth label="Password" name="password" type={showPassword ? 'text' : 'password'} value={formData.password} onChange={handleInputChange} error={!!errors.password} helperText={errors.password} required InputProps={{ endAdornment: (<InputAdornment position="end"><IconButton onClick={() => setShowPassword(!showPassword)} edge="end">{showPassword ? <VisibilityOff /> : <Visibility />}</IconButton></InputAdornment>) }} />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField fullWidth label="Confirm Password" name="confirmPassword" type="password" value={formData.confirmPassword} onChange={handleInputChange} error={!!errors.confirmPassword} helperText={errors.confirmPassword} required />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <TextField fullWidth label="Phone Number" name="phone" value={formData.phone} onChange={handleInputChange} error={!!errors.phone} helperText={errors.phone} required />
                            </Grid>
                            <Grid item xs={12} md={6}>
                                <FormControl fullWidth>
                                    <InputLabel>Country</InputLabel>
                                    <Select name="country" value={formData.country} onChange={handleInputChange} label="Country">
                                        <MenuItem value="SA">Saudi Arabia</MenuItem>
                                        <MenuItem value="AE">United Arab Emirates</MenuItem>
                                        <MenuItem value="QA">Qatar</MenuItem>
                                        <MenuItem value="KW">Kuwait</MenuItem>
                                        <MenuItem value="BH">Bahrain</MenuItem>
                                        <MenuItem value="OM">Oman</MenuItem>
                                    </Select>
                                </FormControl>
                            </Grid>
                        </Grid>
                    </Box>
                );
            case 2:
                return (
                    <Box sx={{ mt: 4 }}>
                        <Typography variant="h5" gutterBottom>
                            {userType === 'shipper' ? 'Shipper Information' : userType === 'carrier' ? 'Carrier Information' : 'Broker Information'}
                        </Typography>
                        {userType === 'shipper' && (
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    <TextField fullWidth label="Company Name" name="companyName" value={formData.companyName} onChange={handleInputChange} />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <FormControl fullWidth>
                                        <InputLabel>Industry</InputLabel>
                                        <Select name="industry" value={formData.industry} onChange={handleInputChange} label="Industry">
                                            <MenuItem value="retail">Retail trade</MenuItem>
                                            <MenuItem value="manufacturing">Manufacturing</MenuItem>
                                            <MenuItem value="construction">Construction</MenuItem>
                                            <MenuItem value="food">Foodstuffs</MenuItem>
                                            <MenuItem value="electronics">Electronics</MenuItem>
                                            <MenuItem value="other">Other</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <FormControl fullWidth>
                                        <InputLabel>Monthly shipping volume</InputLabel>
                                        <Select name="shippingVolume" value={formData.shippingVolume} onChange={handleInputChange} label="Monthly shipping volume">
                                            <MenuItem value="low">Under 10 shipments</MenuItem>
                                            <MenuItem value="medium">10-50 shipments</MenuItem>
                                            <MenuItem value="high">50-200 shipments</MenuItem>
                                            <MenuItem value="very-high">Over 200 shipments</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                            </Grid>
                        )}
                        {userType === 'carrier' && (
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    <TextField fullWidth label="Transport company name" name="carrierName" value={formData.carrierName} onChange={handleInputChange} required />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField fullWidth label="Commercial license number" name="licenseNumber" value={formData.licenseNumber} onChange={handleInputChange} required />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <FormControl fullWidth>
                                        <InputLabel>Fleet size</InputLabel>
                                        <Select name="fleetSize" value={formData.fleetSize} onChange={handleInputChange} label="Fleet size">
                                            <MenuItem value="small">1-5 vehicles</MenuItem>
                                            <MenuItem value="medium">6-20 vehicles</MenuItem>
                                            <MenuItem value="large">21-50 vehicles</MenuItem>
                                            <MenuItem value="xlarge">More than 50 vehicles</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                                <Grid item xs={12}>
                                    <TextField fullWidth label="Geographical areas covered" name="serviceAreas" value={formData.serviceAreas} onChange={handleInputChange} placeholder="Example: Riyadh, Jeddah, Dammam" helperText="Separate regions with a comma" />
                                </Grid>
                            </Grid>
                        )}
                        {userType === 'broker' && (
                            <Grid container spacing={3}>
                                <Grid item xs={12}>
                                    <TextField fullWidth label="Brokerage name" name="brokerageName" value={formData.brokerageName} onChange={handleInputChange} required />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <TextField fullWidth label="License number" name="licenseNumber" value={formData.licenseNumber} onChange={handleInputChange} required />
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <FormControl fullWidth>
                                        <InputLabel>Years of experience</InputLabel>
                                        <Select name="yearsExperience" value={formData.yearsExperience} onChange={handleInputChange} label="Years of experience">
                                            <MenuItem value="0-2">Less than two years</MenuItem>
                                            <MenuItem value="2-5">2-5 years</MenuItem>
                                            <MenuItem value="5-10">5-10 years</MenuItem>
                                            <MenuItem value="10+">more than 10 years</MenuItem>
                                        </Select>
                                    </FormControl>
                                </Grid>
                            </Grid>
                        )}
                        <Alert severity="info" sx={{ mt: 3 }}>
                            <Typography variant="body2">This information helps us personalize your experience and provide the right features for your role.</Typography>
                        </Alert>
                    </Box>
                );
            case 3:
                return (
                    <Box sx={{ mt: 4 }}>
                        <Typography variant="h5" gutterBottom>Review and confirm information</Typography>
                        <Paper sx={{ p: 3, mb: 3 }}>
                            <Typography variant="h6" color="primary" gutterBottom>Registration summary</Typography>
                            <Grid container spacing={2}>
                                <Grid item xs={12} md={6}>
                                    <Typography variant="body2" color="text.secondary">User type:</Typography>
                                    <Typography variant="body1" sx={{ fontWeight: 'bold' }}>{userTypes.find(t => t.value === userType)?.label}</Typography>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Typography variant="body2" color="text.secondary">Email:</Typography>
                                    <Typography variant="body1">{formData.email}</Typography>
                                </Grid>
                                <Grid item xs={12} md={6}>
                                    <Typography variant="body2" color="text.secondary">Phone:</Typography>
                                    <Typography variant="body1">{formData.phone}</Typography>
                                </Grid>
                                {userType === 'shipper' && formData.companyName && (
                                    <Grid item xs={12} md={6}>
                                        <Typography variant="body2" color="text.secondary">Company name:</Typography>
                                        <Typography variant="body1">{formData.companyName}</Typography>
                                    </Grid>
                                )}
                                {userType === 'carrier' && formData.carrierName && (
                                    <Grid item xs={12} md={6}>
                                        <Typography variant="body2" color="text.secondary">Transport company:</Typography>
                                        <Typography variant="body1">{formData.carrierName}</Typography>
                                    </Grid>
                                )}
                                {userType === 'broker' && formData.brokerageName && (
                                    <Grid item xs={12} md={6}>
                                        <Typography variant="body2" color="text.secondary">Brokerage Name:</Typography>
                                        <Typography variant="body1">{formData.brokerageName}</Typography>
                                    </Grid>
                                )}
                            </Grid>
                        </Paper>
                        <Alert severity="warning" sx={{ mb: 3 }}>
                            <Typography variant="body2"><strong>Warning:</strong> Your account will be <strong>pending</strong> until it is reviewed by the platform administration. The review may take 1-3 business days.</Typography>
                        </Alert>
                        {errors.submit && (
                            <Alert severity="error" sx={{ mb: 3 }}>{errors.submit}</Alert>
                        )}
                    </Box>
                );
            default:
                return null;
        }
    };
    return (
        <PortalBackground>
            <div className="auth-window">
                {success ? (
                    <Container maxWidth="md" sx={{ p: 0 }}>
                        <Paper sx={{ p: 6, textAlign: 'center', boxShadow: 'none', background: 'transparent' }}>
                            <Box sx={{ mb: 4 }}><CheckCircle sx={{ fontSize: 80, color: 'success.main' }} /></Box>
                            <Typography variant="h4" gutterBottom color="success.main">Registration request received successfully!</Typography>
                            <Typography variant="body1" paragraph sx={{ mb: 3 }}>Thank you for registering in the transportation management system (TMS). Your application is currently under review by the platform administration.</Typography>
                            <Typography variant="body2" color="text.secondary" paragraph>You will receive an email when your account is activated. The process can take 1-3 business days.</Typography>
                            <Button variant="contained" href="/login" sx={{ mt: 2 }}>Go to login page</Button>
                        </Paper>
                    </Container>
                ) : (
                    <Container maxWidth="md" sx={{ p: 0 }}>
                        <Paper sx={{ p: { xs: 3, md: 6 }, boxShadow: 'none', background: 'transparent' }}>
                            <Box sx={{ textAlign: 'center', mb: 4 }}>
                                <Typography variant="h4" component="h1" color="primary" gutterBottom>Transportation management system (TMS) - Registration</Typography>
                                <Typography variant="body1" color="text.secondary">Join the integrated transportation platform and get features tailored to you</Typography>
                            </Box>
                            <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
                                {steps.map((label) => (<Step key={label}><StepLabel>{label}</StepLabel></Step>))}
                            </Stepper>
                            {renderStepContent()}
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                                <Button disabled={activeStep === 0} onClick={handleBack} variant="outlined">Back</Button>
                                {activeStep === steps.length - 1 ? (
                                    <Button variant="contained" onClick={handleSubmit} disabled={submitting} startIcon={submitting ? null : <CheckCircle />}>{submitting ? 'Sending...' : 'Confirm registration'}</Button>
                                ) : (
                                    <Button variant="contained" onClick={handleNext} disabled={activeStep === 0 && !userType}>Next</Button>
                                )}
                            </Box>
                            <Box sx={{ mt: 4, pt: 3, borderTop: '1px solid #e5e7eb', textAlign: 'center' }}>
                                <Typography variant="body2" color="text.secondary">Already have an account?{' '}<Button href="/login" size="small">Log in here</Button></Typography>
                            </Box>
                        </Paper>
                    </Container>
                )}
            </div>
            <div className="text-center text-xs text-slate-500 mt-6">
                <p>Secure workspace. Authorization is required.</p>
            </div>
            <div className="flex w-full max-w-6xl items-center justify-between text-[10px] text-slate-400 gap-4 mt-2">
                <span>Copyright 2006 Gabani Transport Solutions</span>
                <span>Enterprise Workspace</span>
            </div>
        </PortalBackground>
    );
};

export default TMSRegister;
