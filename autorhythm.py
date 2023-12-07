import librosa as lib
import tkinter as tk
import turtle, random
from pygame import mixer

class Autorhythmic:
    def __init__(self, canvas, single_note, hole, filename):
        self.canvas = canvas
        self.single_note = single_note
        self.hole = hole
        self.notes = []  # 노트를 저장할 리스트 추가

        # Initialize a hole.
        self.hole.shape('square')
        self.hole.color('black')
        self.hole.penup()

        # Instantiate a turtle for printing point.
        self.pointer = turtle.RawTurtle(canvas)
        self.pointer.hideturtle()
        self.pointer.penup()

        self.indicator = turtle.RawTurtle(canvas)
        self.indicator.hideturtle()
        self.indicator.penup()

        self.point = 0
        self.amount_notes = 0
        self.prev_dist = 0
        self.filename = filename
        self.note_passed = False

        # 스페이스바를 누를 때마다 판정 및 포인트 계산 함수를 호출하도록 설정
        self.canvas.listen()
        self.canvas.onkeypress(self.calculate_score, 'space')

    def calculate_score(self):
        # 노트와 홀의 좌표를 얻어 판정 계산
        self.notes[0].forward(0)
        p = self.hole.pos()
        q = self.notes[0].pos()  # 여기서는 첫 번째 노트의 좌표를 사용했습니다. 필요에 따라 수정하세요.
        dx, dy = p[0] - q[0], p[1] - q[1]
            
        hole_size = 1 # 적절한 홀 크기로 수정하세요

        if 0.1< dx**2 + dy**2 <= hole_size*1:
            judgment = 'perfect'
        elif dx**2 + dy**2 <= hole_size*1.5:
            judgment = 'good'
        elif dx**2 + dy**2 <= hole_size*2:
            judgment = 'bad'
        elif  dx**2 + dy**2 > hole_size*2:
            judgment = 'break'

        # 판정에 따라 포인트 증가 및 노트 제거
        if judgment == 'perfect':
            self.point += 10
        elif judgment == 'good':
            self.point += 5
        elif judgment == 'bad':
            self.point += 2
        else:
            self.point -= 5  # 예시로, 브레이크 판정일 때 포인트 감점

        self.notes[0].reset()
        removed_note = self.notes.pop(0)
        removed_note.clear()
        removed_note.hideturtle()
        self.amount_notes -= 1

    def writepoint(self):
        self.pointer.undo()
        self.pointer.penup()
        self.pointer.setpos(300, 300)
        self.pointer.write(f'point: {self.point}', align='center', font=('Arial', 16, 'normal'))
        self.canvas.ontimer(self.writepoint, 100)

    def start(self, beat_times):
        self.hole.setpos(0, 0)  
        self.hole.setheading(0)
        mixer.init()
        mixer.music.set_volume(0.3)
        mixer.music.load(filename)
        self.create_and_move_notes(beat_times)
        self.show_notes()
        self.writepoint()
        self.indicate(beat_times)
        self.hole.write('Game Starts after 3s!')
        self.canvas.ontimer(lambda: self.hole.reset(),3000)
        self.canvas.ontimer(self.move_notes, 3000)
        self.canvas.ontimer(mixer.music.play(1),3000)

    def create_and_move_notes(self, beat_times):
        # Locate notes randomly and store them in the list
        self.single_note.speed(0)
        self.hole.write('Please wait.. Generating notes.')
        self.notes = [self.create_note(beat_time) for beat_time in beat_times]
        self.hole.reset()
        self.amount_notes = len(self.notes)

    def create_note(self, beat_time):
        new_note = self.single_note.clone()
        new_note.shape("square")
        new_note.color("blue")
        new_note.penup()
        new_note.hideturtle()
        new_note.shapesize(stretch_wid=1, stretch_len=0.3)
        new_note.speed(0)  # 애니메이션 속도를 0으로 설정하여 즉시 이동
        mode = random.randint(0, 3)
        if mode == 0:
            new_note.setpos(beat_time*1000- self.prev_dist, 0)
            new_note.setheading(180)
        elif mode == 1:
            new_note.setpos(0, beat_time*1000- self.prev_dist)
            new_note.setheading(270)
        elif mode == 2:
            new_note.setpos(-beat_time*1000+ self.prev_dist, 0)
            new_note.setheading(0)
        else:
            new_note.setpos(0, -beat_time*1000+ self.prev_dist)
            new_note.setheading(90)
        self.prev_dist += new_note.distance(0,0)
        self.notes.append(new_note)  # 리스트에 노트 추가
        self.amount_notes += 1
        return new_note

    def indicate(self, beat_times):
        self.indicator.undo()
        self.indicator.penup()
        self.indicator.setpos(100, -200)
        self.indicator.write(f'notes: {self.amount_notes} / {len(beat_times)}', align='center', font=('Arial', 16, 'normal'))
        self.canvas.ontimer(lambda: self.indicate(beat_times), 100)

    def move_notes(self):
        self.notes[0].fd(10)
    
        if not self.note_passed and self.notes[0].distance(0, 0) < 2:
            self.note_passed = True
        if(self.note_passed is True and self.notes[0].distance(0,0) > 2):
            self.calculate_score()
            self.note_passed = False
        self.canvas.ontimer(lambda: self.move_notes(),10)
    
    def show_notes(self):
        for i, note in enumerate(self.notes):
            if i<5:
                note.showturtle()
        self.canvas.ontimer(self.show_notes,10)

class notemove(turtle.RawTurtle):
    def __init__(self, canvas):
        super().__init__(canvas)

class holemove(turtle.RawTurtle):
    def __init__(self, canvas):
        super().__init__(canvas)

if __name__ == '__main__':
    # Get the file path to an included audio example
    print('Loading...')
    filename = 'M31.mp3'
    
    y, sr = lib.load(filename)
    playtime = lib.get_duration(y=y,sr=sr)
    
    tempo, beat_frames = lib.beat.beat_track(y=y, sr=sr)

    print('Estimated tempo: {:.2f} bpm'.format(tempo))
    print(f'Duration: {playtime}s')
    onset_env = lib.onset.onset_strength(y=y, sr=sr)
    
    # 온셋을 감지합니다.
    beat_times = lib.onset.onset_detect(onset_envelope=onset_env, sr=sr, units='time')
    
    print('notes: ',len(beat_times))
    root = tk.Tk()
    canvas = tk.Canvas(root, width=1000, height=1000)
    canvas.pack()
    canvas.create_rectangle(0,0,canvas.winfo_reqwidth(), canvas.winfo_reqheight(), fill='aliceblue', outline='aliceblue')
    screen = turtle.TurtleScreen(canvas)

    note = notemove(screen)
    hole = holemove(screen)

    game = Autorhythmic(screen, note, hole, filename)
    game.start(beat_times)
    screen.mainloop()