# Bubble Sort
def Bubble(A:list , N=None):
    if N is None:
        N = len(A)
    
    for i in range(N-1):
        if A[i] > A[i+1]: A[i],A[i+1] = A[i+1],A[i]
    if N > 1:
        Bubble(A , N-1)
    return A



# Insertion Sort
def Insertion(A:list , start=None, end=None):
    if start is None and end is None:
        start = 1
        end = len(A)
    
    value = A[start]
    loc = start 
    while loc > 0 and A[loc-1] > value:
        A[loc] = A[loc-1]
        loc -= 1
    A[loc] = value 
    if start+1 < end:
        Insertion(A , start+1 , end)
    return A



# Selection Sort
def Selection(A:list , N=None):
    if N is None:
        N = len(A)
    if N > 0:
        SL = SLargest(A , N)
        A[SL],A[N-1] = A[N-1],A[SL]
        Selection(A , N-1)
    return A

def SLargest(A, last:int):
    largest = 0
    for i in range(last):
        if A[i] > A[largest]: largest = i
    return largest



# Merge Sort
def Merge(A:list , B=None , start=None , end=None):
    if B is None and start is None and end is None:
        B = [None]*len(A)
        start = 0
        end = len(A)-1
    if start < end:
        mid = (start + end)//2
        Merge(A , B , start , mid)
        Merge(A , B ,  mid+1 , end)
        MergeCS(A , B , start , mid , end)
    return A

def MergeCS(A , B , start:int , mid:int , end:int):
    front = start
    back = mid+1
    i = 0
    while front <= mid and back <= end:
        if A[front] <= A[back]:
            B[i] = A[front]
            i += 1
            front += 1
        else:
            B[i] = A[back]
            i += 1
            back += 1
    while front <= mid:
        B[i] = A[front]
        i += 1
        front += 1
    while back <= end:
        B[i] = A[back]
        i += 1
        back += 1
    for i in range(start, end+1):
        A[i]=B[i-start]



# Quick Sort
def Quick(A:list , div=None , std=None):
    if div is None and std is None:
        div = 0
        std = len(A)-1
    if div < std:
        mid = partition(A , div , std)
        Quick(A , div , mid-1)
        Quick(A , mid+1 , std)
    return A

def partition(A:list , div:int , std:int) -> int:
    Stdvalue = A[std]
    FEnd = div-1
    for SStart in range(div,std):
        if A[SStart] <= Stdvalue:
            FEnd += 1
            A[FEnd],A[SStart] = A[SStart],A[FEnd]
    A[FEnd+1],A[std] = A[std],A[FEnd+1]
    return FEnd+1



# Heap Sort
def Heap(A:list):
    BuildHeap(A) 
    for last in range(len(A)-1,0,-1):
        A[last], A[0] = A[0], A[last]
        percolateDown(A,0,last-1)
    return A

def BuildHeap(A):
    for i in range((len(A)-2) // 2, -1, -1): percolateDown(A , i , len(A)-1)

def percolateDown(A , start:int , end:int):
    left = 2*start+1
    right = 2*start+2
    if left <= end:
        if right <= end and A[left] < A[right]: left = right
        if A[start] < A[left]:
            A[start], A[left] = A[left], A[start]
            percolateDown(A, left, end)



# Shell Sort
def Shell(A:list):
    G = GapSequence(len(A))
    for gap in G:
        for k in range(gap):
            stepInsertion(A, k, gap)
    return A

def stepInsertion(A , k:int , gap:int):
    for i in range(k + gap , len(A), gap):
        j = i - gap
        newItem = A[i]
        while 0 <= j and newItem < A[j]:
            A[j+gap] = A[j]
            j -= gap
        A[j+gap] = newItem

def GapSequence(n:int) -> list:
    G = [1]
    gap = 1
    while gap < n/5:
        gap = 3*gap + 1
        G.append(gap)
    G.reverse()
    return G
