//
//  MagStripe.h
//  KegBoard
//
//  Created by John Boiles on 9/25/10.
//
//  This program is free software; you can redistribute it and/or
//  modify it under the terms of the GNU General Public License
//  as published by the Free Software Foundation; either version 2
//  of the License, or (at your option) any later version.

//  This program is distributed in the hope that it will be useful,
//  but WITHOUT ANY WARRANTY; without even the implied warranty of
//  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//  GNU General Public License for more details.
//
//  You should have received a copy of the GNU General Public License
//  along with this program.  If not, see <http://www.gnu.org/licenses/>.
//

#include <inttypes.h>

#define MAGSTRIPE_DEBUG 0
#define MAGSTRIPE_BUFFER_SIZE 250

class MagStripe {
  public:
    MagStripe(uint8_t clockPin, uint8_t dataPin, uint8_t cardPresentPin);
    bool dataAvailable;
    void reset();
    int getData(uint8_t **data);
    void clockData();
  private:
    // TODO(johnb): Make this some sort of bit vector so we more efficiently use ram.
    volatile uint8_t _buffer[MAGSTRIPE_BUFFER_SIZE];
    volatile int _bufferIndex;
    // Buffer for data, though this sucks since each uint8_t only uses a bit
    uint8_t _cardData[40]; // holds card id string
    int _dataSize; // length of card id string
    uint8_t _clockPin;
    uint8_t _dataPin;
    uint8_t _cardPresentPin;
    int findStartSentinal();
    void decode();
    uint8_t saveByte(uint8_t thisByte[]);
    uint8_t decodeByte(uint8_t thisByte[]);
    void printBuffer();
};

