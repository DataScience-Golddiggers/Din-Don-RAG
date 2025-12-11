import { Request, Response } from 'express';

export const renderHome = (req: Request, res: Response) => {
    res.render('home', { title: 'Home' });
};

export const renderChat = (req: Request, res: Response) => {
    res.render('chat', { title: 'Chat' });
};

export const renderLegacyChat = (req: Request, res: Response) => {
    res.render('legacy_chat', { title: 'Legacy Chat' });
};

export const renderAbout = (req: Request, res: Response) => {
    res.render('about', { title: 'About Us' });
};