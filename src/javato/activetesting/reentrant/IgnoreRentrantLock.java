package javato.activetesting.reentrant;

import java.util.Set;

/**
 * Copyright (c) 2007-2008,
 * Koushik Sen    <ksen@cs.berkeley.edu>
 * All rights reserved.
 * <p/>
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met:
 * <p/>
 * 1. Redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer.
 * <p/>
 * 2. Redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution.
 * <p/>
 * 3. The names of the contributors may not be used to endorse or promote
 * products derived from this software without specific prior written
 * permission.
 * <p/>
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
 * IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
 * TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
 * PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
 * OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */
public class IgnoreRentrantLock {
    public static ThreadLocal lockSet = new ThreadLocal() {
        public Object initialValue() {
            return new LockSetWithCount();
        }
    };

    /**
     * @param thread
     * @param lock   is the id of the object about to be acquired
     * @return true iff the thread will actually acquire the lock (and not re-acquire it.)
     */
    public boolean lockBefore(Integer thread, Integer lock) {
        return ((LockSetWithCount) lockSet.get(thread)).add(lock);
    }

    /**
     * @param thread
     * @param lock   is the id of the object about to be acquired
     * @return true iff the thread will actually acquire the lock (and not re-acquire it.)
     */
    public boolean isReentrant(Integer thread, Integer lock) {
        if (((LockSetWithCount) lockSet.get(thread)).getLockSet().contains(lock))
            return true;
        else
            return false;
    }

    /**
     * @param thread
     * @param lock   is the id of the object about to be acquired
     * @return true iff the thread will actually acquire the lock (and not re-acquire it.)
     */
    public boolean canLock(Integer thread, Integer lock, Set<Integer> threadSet) {
        for (Integer threadPrime : threadSet) {
            if (thread.equals(threadPrime))
                continue;
            
            // System.out.println("\tthread: " + thread + ", lock: " + lock + ", threadPrime: " + threadPrime);
            // for (Integer locks : ((LockSetWithCount) lockSet.get(threadPrime)).getLockSet()) {
            //     System.out.println("\theld lock: " + locks);
            // }

            if (((LockSetWithCount) lockSet.get(threadPrime)).getLockSet().contains(lock))
                return false;
        }
        return true;
    }

    /**
     * @param thread
     * @param lock   is the id of the object that has been released
     * @return true iff the thread have actually released the lock
     */

    public boolean unlockAfter(Integer thread, Integer lock) {
        return ((LockSetWithCount) lockSet.get(thread)).remove(lock);
    }
}
