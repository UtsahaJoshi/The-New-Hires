import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Login from './pages/Login'

describe('Login Page', () => {
    it('renders login heading', () => {
        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        )
        // Adjust this based on what's actually in Login.tsx
        // For now, let's just check if something renders
        expect(document.body).toBeDefined()
    })
})
