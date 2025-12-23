#include <graphics.h>
#include <conio.h>
#include <dos.h>     // for delay()
#include <stdlib.h>  // for exit()

// Function to draw a simple jet at position (x, y)
void drawJet(int x, int y) {
    setcolor(WHITE);
    setfillstyle(SOLID_FILL, WHITE);

    // Body of the jet
    rectangle(x, y, x + 100, y + 20);
    floodfill(x + 1, y + 1, WHITE);

    // Tail fin
    line(x + 100, y + 10, x + 120, y);
    line(x + 100, y + 10, x + 120, y + 20);

    // Nose
    line(x, y, x - 20, y + 10);
    line(x - 20, y + 10, x, y + 20);

    // Window (just for aesthetics)
    setfillstyle(SOLID_FILL, BLUE);
    fillellipse(x + 30, y + 10, 5, 5);
    fillellipse(x + 50, y + 10, 5, 5);
}

int main() {
    int gd = DETECT, gm;
    initgraph(&gd, &gm, "");

    // Set background to blue to simulate sky
    setbkcolor(BLUE);
    cleardevice();

    // Animate the jet flying from left to right
    for (int x = 0; x < getmaxx(); x += 5) {
        cleardevice();           // Clear screen each frame
        drawJet(x, 200);         // Draw jet at new position
        delay(30);               // Small delay to control speed
    }

    // After animation
    outtextxy(getmaxx() / 2 - 100, getmaxy() - 30, "Press any key to exit...");
    getch();
    closegraph();
    return 0;
}
